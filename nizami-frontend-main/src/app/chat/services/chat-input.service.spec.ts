import { TestBed } from '@angular/core/testing';

import { ChatInputService } from './chat-input.service';

describe('ChatInputService', () => {
  let service: ChatInputService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ChatInputService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
