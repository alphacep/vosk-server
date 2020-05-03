package main

import (
	"encoding/json"
	"github.com/gorilla/websocket"
	log "github.com/sirupsen/logrus"
	"io"
	"net/url"
	"os"
)

const Host = "localhost"
const Port = "2700"
const buffsize = 8000

type Message struct {
	Result []struct {
		Conf  float64
		End   float64
		Start float64
		Word  string
	}
	Text string
}

var m Message

func main() {

	if len(os.Args) < 2 {
		panic("Please specify second argument")
	}

	u := url.URL{Scheme: "ws", Host: Host + ":" + Port, Path: ""}
	log.Info("connecting to ", u.String())

	// Opening websocket connection
	c, _, err := websocket.DefaultDialer.Dial(u.String(), nil)
	check(err)
	defer c.Close()

	f, err := os.Open(os.Args[1])
	check(err)

	for {
		buf := make([]byte, buffsize)
		dat, err := f.Read(buf)

		if dat == 0 && err == io.EOF {
			err = c.WriteMessage(websocket.TextMessage, []byte("{\"eof\" : 1}"))
			check(err)
			break
		}
		check(err)

		err = c.WriteMessage(websocket.BinaryMessage, buf)
		check(err)

		// Read message from server
		_, _, err = c.ReadMessage()
		check(err)
	}

	// Read final message from server
	_, msg, err := c.ReadMessage()
	check(err)

	// Closing websocket connection
	c.WriteMessage(websocket.CloseMessage, websocket.FormatCloseMessage(websocket.CloseNormalClosure, ""))

	// Unmarshalling received message
	err = json.Unmarshal(msg, &m)
	check(err)
	log.Info(m.Text)
}

func check(err error) {

	if err != nil {
		log.Error(err)
	}
}
