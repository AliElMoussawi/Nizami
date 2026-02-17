import {Component, ElementRef, OnDestroy, OnInit, input, signal, effect} from '@angular/core';
import {ChatSystemProfileComponent} from '../chat-system-profile/chat-system-profile.component';

interface ThinkingStep {
  en: string;
  ar: string;
}

const THINKING_STEPS: ThinkingStep[] = [
  {en: 'Thinking...', ar: 'جارٍ التفكير...'},
  {en: 'Analyzing your question...', ar: 'جارٍ تحليل سؤالك...'},
  {en: 'Searching legal documents...', ar: 'جارٍ البحث في الوثائق القانونية...'},
  {en: 'Reviewing relevant laws...', ar: 'جارٍ مراجعة القوانين ذات الصلة...'},
  {en: 'Summarizing the answer...', ar: 'جارٍ تلخيص الإجابة...'},
  {en: 'Preparing your answer...', ar: 'جارٍ إعداد الإجابة...'},
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
  language = input<'ar' | 'en'>('ar');

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
