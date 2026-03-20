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

import { Injectable, signal } from '@angular/core';
import { Subject } from 'rxjs';
import { A2uiMessage } from '@a2ui/web_core/v0_9';

/** A payload wrapper for data sent from the A2UI server to the client. */
export interface A2DataPayload {
  kind: 'data';
  data: A2uiMessage;
}

/** A payload wrapper for text sent from the A2UI server to the client. */
export interface A2TextPayload {
  kind: 'text';
  text: string;
}

/** The raw payload format for messages from the v0.9 A2UI server. */
export type A2AServerPayload =
  | Array<A2DataPayload | A2TextPayload>
  | { error: string };

@Injectable({ providedIn: 'root' })
export class Client {
  readonly isLoading = signal(false);
  readonly messages$ = new Subject<A2uiMessage[]>();

  constructor() {}

  async makeRequest(request: any) {
    let messages: A2uiMessage[];

    try {
      this.isLoading.set(true);
      const response = await this.send(request);
      messages = response;
    } catch (err) {
      console.error(err);
      throw err;
    } finally {
      this.isLoading.set(false);
    }

    this.messages$.next(messages);
    return messages;
  }

  async send(message: any): Promise<A2uiMessage[]> {
    const response = await fetch('/a2a', {
      body: JSON.stringify(message),
      method: 'POST',
    });

    if (response.ok) {
      const data = (await response.json()) as A2AServerPayload;
      const messages: A2uiMessage[] = [];

      if ('error' in data) {
        throw new Error(data.error);
      } else {
        for (const item of data) {
          if (item.kind === 'text') continue;
          messages.push(item.data);
        }
      }
      return messages;
    }

    const error = (await response.json()) as { error: string };
    throw new Error(error.error);
  }
}
