/*
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Chat } from './chat';
import { A2A_SERVICE } from '../../interfaces/a2a-service';

describe('Chat', () => {
  let component: Chat;
  let fixture: ComponentFixture<Chat>;

  beforeEach(async () => {
    const mockA2aService = {
      sendMessage: jasmine.createSpy('sendMessage').and.returnValue(Promise.resolve({})),
      getAgentCard: jasmine.createSpy('getAgentCard').and.returnValue(Promise.resolve({})),
    };

    await TestBed.configureTestingModule({
      imports: [Chat],
      providers: [{ provide: A2A_SERVICE, useValue: mockA2aService }],
    }).compileComponents();

    fixture = TestBed.createComponent(Chat);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
