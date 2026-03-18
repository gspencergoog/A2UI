import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';
import { SurfaceGroupAction } from '@a2ui/web_core/v0_9';

@Injectable({ providedIn: 'root' })
export class ActionDispatcher {
  private action$ = new Subject<SurfaceGroupAction>();
  actions = this.action$.asObservable();

  dispatch(action: SurfaceGroupAction) {
    this.action$.next(action);
  }
}
