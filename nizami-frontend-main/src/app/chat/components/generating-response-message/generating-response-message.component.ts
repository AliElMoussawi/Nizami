import {Component, ElementRef, OnDestroy, OnInit, input, signal, effect} from '@angular/core';
import {ChatSystemProfileComponent} from '../chat-system-profile/chat-system-profile.component';

interface ThinkingStep {
  [key: string]: string;
  en: string;
  ar: string;
  fr: string;
  hi: string;
  ur: string;
}

const THINKING_STEPS: ThinkingStep[] = [
  {en: 'Thinking...', ar: 'جارٍ التفكير...', fr: 'Réflexion en cours...', hi: 'सोच रहा है...', ur: '...سوچ رہا ہے'},
  {en: 'Analyzing your question...', ar: 'جارٍ تحليل سؤالك...', fr: 'Analyse de votre question...', hi: 'आपके प्रश्न का विश्लेषण हो रहा है...', ur: '...آپ کے سوال کا تجزیہ ہو رہا ہے'},
  {en: 'Searching legal documents...', ar: 'جارٍ البحث في الوثائق القانونية...', fr: 'Recherche dans les documents juridiques...', hi: 'कानूनी दस्तावेज़ों में खोज हो रही है...', ur: '...قانونی دستاویزات میں تلاش ہو رہی ہے'},
  {en: 'Reviewing relevant laws...', ar: 'جارٍ مراجعة القوانين ذات الصلة...', fr: 'Examen des lois pertinentes...', hi: 'संबंधित कानूनों की समीक्षा हो रही है...', ur: '...متعلقہ قوانین کا جائزہ لیا جا رہا ہے'},
  {en: 'Summarizing the answer...', ar: 'جارٍ تلخيص الإجابة...', fr: 'Résumé de la réponse...', hi: 'उत्तर का सारांश तैयार हो रहा है...', ur: '...جواب کا خلاصہ تیار ہو رہا ہے'},
  {en: 'Preparing your answer...', ar: 'جارٍ إعداد الإجابة...', fr: 'Préparation de votre réponse...', hi: 'आपका उत्तर तैयार हो रहा है...', ur: '...آپ کا جواب تیار ہو رہا ہے'},
];

@Component({
  selector: 'app-generating-response-message',
  templateUrl: './generating-response-message.component.html',
  imports: [
    ChatSystemProfileComponent,
  ],
  styleUrl: './generating-response-message.component.scss'
})
export class GeneratingResponseMessageComponent implements OnInit, OnDestroy {
  language = input<string>('ar');

  currentStepText = signal<string>('');
  isTransitioning = signal<boolean>(false);

  private stepIndex = 0;
  private intervalId: ReturnType<typeof setInterval> | null = null;

  constructor(public elementRef: ElementRef) {
    effect(() => {
      const lang = this.language();
      this.currentStepText.set(THINKING_STEPS[this.stepIndex][lang]);
    });
  }

  ngOnInit(): void {
    const lang = this.language();
    this.stepIndex = 0;
    this.currentStepText.set(THINKING_STEPS[0][lang]);

    this.intervalId = setInterval(() => {
      this.advanceStep();
    }, 5500);
  }

  ngOnDestroy(): void {
    if (this.intervalId !== null) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  private advanceStep(): void {
    this.isTransitioning.set(true);

    setTimeout(() => {
      this.stepIndex++;
      if (this.stepIndex >= THINKING_STEPS.length) {
        this.stepIndex = THINKING_STEPS.length - 2;
      }
      const lang = this.language();
      this.currentStepText.set(THINKING_STEPS[this.stepIndex][lang]);
      this.isTransitioning.set(false);
    }, 300);
  }
}
