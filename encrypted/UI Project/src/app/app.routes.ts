import { Routes } from '@angular/router';
import { RechargeComponent } from './pages/recharge/recharge.component';
import { RechargePacksComponent } from './pages/recharge-packs/recharge-packs.component';
import { PaymentComponent } from './pages/payment/payment.component';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'recharge' },
  { path: 'recharge', component: RechargeComponent, title: 'Recharge' },
  { path: 'recharge-packs', component: RechargePacksComponent, title: 'Recharge Packs' },
  { path: 'payment', component: PaymentComponent, title: 'Payment' },
  { path: '**', redirectTo: 'recharge' }
];
