import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';

import { PlansService, PlanDetail } from '../../core/plans.service';

@Component({
  selector: 'app-payment',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './payment.component.html',
  styleUrl: './payment.component.css'
})
export class PaymentComponent implements OnInit {
  plan: PlanDetail | null = null;
  loading = true;
  error: string | null = null;
  mobileDisplay = '98765 43210';
  showBenefits = false;

  constructor(
    private plansService: PlansService,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    const planId = Number(this.route.snapshot.queryParamMap.get('planId'));
    const mobile = this.route.snapshot.queryParamMap.get('mobile');

    if (mobile) {
      this.mobileDisplay = `${mobile.slice(0, 5)} ${mobile.slice(5)}`;
    }

    if (!planId) {
      this.error = 'No plan selected.';
      this.loading = false;
      return;
    }

    this.plansService.getPlan(planId).subscribe({
      next: (plan) => {
        this.plan = plan;
        this.loading = false;
      },
      error: () => {
        this.error = 'Unable to load payment summary right now.';
        this.loading = false;
      }
    });
  }

  priceLabel(amount: number, currency: string): string {
    const symbol = currency === 'INR' ? '₹' : `${currency} `;
    return `${symbol}${amount}`;
  }

  categoryLabel(plan: PlanDetail): string {
    if (plan.data) {
      return 'Data';
    }
    if (plan.talktime) {
      return 'Talktime';
    }
    return plan.pack_type;
  }

  toggleBenefits(event: Event): void {
    event.preventDefault();
    this.showBenefits = !this.showBenefits;
  }
}
