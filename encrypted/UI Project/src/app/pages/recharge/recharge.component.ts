import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';

import { PlansService, PlanDetail } from '../../core/plans.service';

@Component({
  selector: 'app-recharge',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './recharge.component.html',
  styleUrl: './recharge.component.css'
})
export class RechargeComponent implements OnInit {
  mode: 'form' | 'details' = 'form';

  // form mode
  mobileNumber = '';
  error: string | null = null;

  // details mode
  planId: number | null = null;
  rawMobile = '';
  mobileDisplay = '';
  plan: PlanDetail | null = null;
  loading = false;

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private plansService: PlansService
  ) {}

  ngOnInit(): void {
    const planIdParam = this.route.snapshot.queryParamMap.get('planId');
    const mobileParam = this.route.snapshot.queryParamMap.get('mobile');

    if (planIdParam) {
      this.mode = 'details';
      this.planId = Number(planIdParam);
      this.rawMobile = mobileParam ?? '';
      this.mobileDisplay = this.rawMobile
        ? `${this.rawMobile.slice(0, 5)} ${this.rawMobile.slice(5)}`
        : '';
      this.loadPlan(this.planId);
    }
  }

  private loadPlan(planId: number): void {
    this.loading = true;
    this.error = null;

    this.plansService.getPlan(planId).subscribe({
      next: (plan) => {
        this.plan = plan;
        this.loading = false;
      },
      error: () => {
        this.error = 'Unable to load plan details right now.';
        this.loading = false;
      }
    });
  }

  goToPacks(): void {
    const trimmed = this.mobileNumber.trim();

    if (!/^\d{10}$/.test(trimmed)) {
      this.error = 'Enter a valid 10-digit mobile number';
      return;
    }

    this.error = null;
    this.router.navigate(['/recharge-packs'], { queryParams: { mobile: trimmed } });
  }

  backToPacks(event: Event): void {
    event.preventDefault();
    this.router.navigate(['/recharge-packs'], { queryParams: { mobile: this.rawMobile } });
  }

  priceLabel(amount: number, currency: string): string {
    const symbol = currency === 'INR' ? '₹' : `${currency} `;
    return `${symbol} ${amount}`;
  }

  payNow(): void {
    if (!this.planId) {
      return;
    }

    this.router.navigate(['/payment'], {
      queryParams: { planId: this.planId, mobile: this.rawMobile }
    });
  }
}
