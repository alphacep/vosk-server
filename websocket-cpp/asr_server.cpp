//------------------------------------------------------------------------------
//
// Based on https://www.boost.org/doc/libs/develop/libs/beast/example/websocket/server/async/websocket_server_async.cpp
//
//------------------------------------------------------------------------------

#include <boost/beast/core.hpp>
#include <boost/beast/websocket.hpp>
#include <boost/asio/dispatch.hpp>
#include <boost/asio/strand.hpp>
#include <algorithm>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <memory>
#include <string>
#include <thread>
#include <vector>
#include <string_view>

#include "vosk_api.h"

namespace beast = boost::beast;         // from <boost/beast.hpp>
namespace http = beast::http;           // from <boost/beast/http.hpp>
namespace websocket = beast::websocket; // from <boost/beast/websocket.hpp>
namespace net = boost::asio;            // from <boost/asio.hpp>
using tcp = boost::asio::ip::tcp;       // from <boost/asio/ip/tcp.hpp>

//------------------------------------------------------------------------------
static VoskModel *model;

struct Args
{
    float sample_rate = 8000;
    int max_alternatives = 0;
    bool show_words = true;
};

// Report a failure
void fail(beast::error_code ec, char const *what)
{
    std::cerr << what << ": " << ec.message() << "\n";
}

// Echoes back all received WebSocket messages
class session : public std::enable_shared_from_this<session>
{
    struct Chunk
    {
        std::string_view result;
        bool stop = false;
    };

    websocket::stream<beast::tcp_stream> ws_;
    beast::flat_buffer buffer_;
    VoskRecognizer *rec_;
    Chunk chunk_;
    Args args_;

public:
    // Take ownership of the socket
    explicit session(tcp::socket &&socket, Args &&args)
        : ws_(std::move(socket)), args_(std::move(args))

    {
        rec_ = vosk_recognizer_new(model, args.sample_rate);
        vosk_recognizer_set_max_alternatives(rec_, args.max_alternatives);
        vosk_recognizer_set_words(rec_, args.show_words);
    }

    ~session()
    {
        vosk_recognizer_free(rec_);
    }

    // Get on the correct executor
    void
    run()
    {
        // We need to be executing within a strand to perform async operations
        // on the I/O objects in this session. Although not strictly necessary
        // for single-threaded contexts, this example code is written to be
        // thread-safe by default.
        net::dispatch(ws_.get_executor(),
                      beast::bind_front_handler(
                          &session::on_run,
                          shared_from_this()));
    }

    // Start the asynchronous operation
    void
    on_run()
    {
        // We output only text
        ws_.text(true);

        // Set suggested timeout settings for the websocket
        ws_.set_option(
            websocket::stream_base::timeout::suggested(
                beast::role_type::server));

        // Set a decorator to change the Server of the handshake
        ws_.set_option(websocket::stream_base::decorator(
            [](websocket::response_type &res)
            {
                res.set(http::field::server,
                        std::string(BOOST_BEAST_VERSION_STRING) +
                            " websocket-server-async");
            }));
        // Accept the websocket handshake
        ws_.async_accept(
            beast::bind_front_handler(
                &session::on_accept,
                shared_from_this()));
    }

    void
    on_accept(beast::error_code ec)
    {
        if (ec)
            return fail(ec, "accept");

        // Read a message
        do_read();
    }

    void
    do_read()
    {
        // Read a message into our buffer
        ws_.async_read(
            buffer_,
            beast::bind_front_handler(
                &session::on_read,
                shared_from_this()));
    }

    Chunk process_chunk(const char *message, int len)
    {
        if (strcmp(message, "{\"eof\" : 1}") == 0)
        {
            return Chunk{vosk_recognizer_final_result(rec_), true};
        }
        else if (vosk_recognizer_accept_waveform(rec_, message, len))
        {
            return Chunk{vosk_recognizer_result(rec_), false};
        }
        else
        {
            return Chunk{vosk_recognizer_partial_result(rec_), false};
        }
    }

    void
    on_read(
        beast::error_code ec,
        std::size_t bytes_transferred)
    {
        boost::ignore_unused(bytes_transferred);

        // This indicates that the session was closed
        if (ec == websocket::error::closed)
            return;

        if (ec)
            fail(ec, "read");

        if (chunk_.stop)
        {
            ws_.close(beast::websocket::close_code::normal);

            return;
        }

        const char *buf = boost::asio::buffer_cast<const char *>(buffer_.cdata());
        int len = static_cast<int>(buffer_.size());
        chunk_ = process_chunk(buf, len);

        ws_.async_write(
            boost::asio::const_buffer(chunk_.result.data(), chunk_.result.size()),
            beast::bind_front_handler(
                &session::on_write,
                shared_from_this()));
    }

    void
    on_write(
        beast::error_code ec,
        std::size_t bytes_transferred)
    {
        boost::ignore_unused(bytes_transferred);

        if (ec)
            return fail(ec, "write");

        // Clear the buffer
        buffer_.consume(buffer_.size());

        // Do another read
        do_read();
    }
};

//------------------------------------------------------------------------------

// Accepts incoming connections and launches the sessions
class listener : public std::enable_shared_from_this<listener>
{
    net::io_context &ioc_;
    tcp::acceptor acceptor_;
    Args args_;

public:
    listener(
        net::io_context &ioc,
        tcp::endpoint endpoint,
        Args args)
        : ioc_(ioc), acceptor_(ioc), args_(args)
    {
        beast::error_code ec;

        // Open the acceptor
        acceptor_.open(endpoint.protocol(), ec);
        if (ec)
        {
            fail(ec, "open");
            return;
        }

        // Allow address reuse
        acceptor_.set_option(net::socket_base::reuse_address(true), ec);
        if (ec)
        {
            fail(ec, "set_option");
            return;
        }

        // Bind to the server address
        acceptor_.bind(endpoint, ec);
        if (ec)
        {
            fail(ec, "bind");
            return;
        }

        // Start listening for connections
        acceptor_.listen(
            net::socket_base::max_listen_connections, ec);
        if (ec)
        {
            fail(ec, "listen");
            return;
        }
    }

    // Start accepting incoming connections
    void
    run()
    {
        do_accept();
    }

private:
    void
    do_accept()
    {
        // The new connection gets its own strand
        acceptor_.async_accept(
            net::make_strand(ioc_),
            beast::bind_front_handler(
                &listener::on_accept,
                shared_from_this()));
    }

    void
    on_accept(beast::error_code ec, tcp::socket socket)
    {
        if (ec)
        {
            fail(ec, "accept");
        }
        else
        {
            // Create the session and run it
            std::make_shared<session>(std::move(socket), std::move(args_))->run();
        }

        // Accept another connection
        do_accept();
    }
};

//------------------------------------------------------------------------------

int main(int argc, char *argv[])
{
    // Check command line arguments.
    if (argc != 5)
    {
        std::cerr << "Usage: asr_server <address> <port> <threads> <model-path>\n"
                  << "Example:\n"
                  << "    asr_server 0.0.0.0 8080 1 model_path\n";
        return EXIT_FAILURE;
    }
    auto const address = net::ip::make_address(argv[1]);
    auto const port = static_cast<unsigned short>(std::atoi(argv[2]));
    auto const threads = std::max<int>(1, std::atoi(argv[3]));
    auto const model_path = argv[4];
    model = vosk_model_new(model_path);

    Args args;
    if (const char *env_p = std::getenv("VOSK_SAMPLE_RATE"))
    {
        args.sample_rate = std::stof(env_p);
    }
    if (const char *env_p = std::getenv("VOSK_ALTERNATIVES"))
    {
        args.max_alternatives = std::stoi(env_p);
    }
    if (const char *env_p = std::getenv("VOSK_SHOW_WORDS"))
    {
        args.show_words = strcmp(env_p, "True") == 0;
    }
    // The io_context is required for all I/O
    net::io_context ioc{threads};

    // Create and launch a listening port
    std::make_shared<listener>(ioc, tcp::endpoint{address, port}, args)->run();

    // Run the I/O service on the requested number of threads
    std::vector<std::thread> v;
    v.reserve(threads - 1);
    for (auto i = threads - 1; i > 0; --i)
        v.emplace_back(
            [&ioc]
            {
                ioc.run();
            });
    ioc.run();

    vosk_model_free(model);
    return EXIT_SUCCESS;
}
