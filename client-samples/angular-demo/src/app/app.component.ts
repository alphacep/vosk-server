import { Component } from '@angular/core';
import { ElementRef, ViewChild} from '@angular/core'
import { DictateService } from "./dictate-service";

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  providers: [DictateService]
})

export class AppComponent {

  @ViewChild('results') private results: ElementRef;

  buttonText = 'Start Recognition';
  textDataBase = '';
  textData = '';

  constructor(private dictateService: DictateService) {
  }

  switchSpeechRecognition() {
    if (!this.dictateService.isInitialized()) {
      this.dictateService.init({
        server: "wss://api.alphacephei.com/asr/en/",
        onResults: (hyp) => {
          console.log(hyp);

          this.textDataBase = this.textDataBase + hyp + '\n';
          this.textData = this.textDataBase;
          this.results.nativeElement.scrollTop = this.results.nativeElement.scrollHeight;
        },
        onPartialResults: (hyp) => {
          console.log(hyp);

          this.textData = this.textDataBase + hyp;
        },
        onError: (code, data) => {
          console.log(code, data);
        },
        onEvent: (code, data) => {
          console.log(code, data);
        }
      });
      this.buttonText = 'Stop Recognition';
    } else if (this.dictateService.isRunning()) {
      this.dictateService.resume();
      this.buttonText = 'Stop Recognition';
    } else {
      this.dictateService.pause();
      this.buttonText = 'Start Recognition';
    }
  }
}
