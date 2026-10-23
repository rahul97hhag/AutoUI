import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';

import { PlansService, PlanSummary } from '../../core/plans.service';

@Component({
  selector: 'app-recharge-packs',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './recharge-packs.component.html',
  styleUrl: './recharge-packs.component.css'
})
export class RechargePacksComponent implements OnInit {
  packs: PlanSummary[] = [];
  loading = true;
  error: string | null = null;

  mobileNumber = '98765 43210';
  private rawMobile = '9876543210';

  constructor(
    private plansService: PlansService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    const mobile = this.route.snapshot.queryParamMap.get('mobile');
    if (mobile) {
      this.rawMobile = mobile;
      this.mobileNumber = `${mobile.slice(0, 5)} ${mobile.slice(5)}`;
    }

    this.plansService.getPlans().subscribe({
      next: (plans) => {
        this.packs = plans;
        this.loading = false;
      },
      error: () => {
        this.error = 'Unable to load recharge packs right now.';
        this.loading = false;
      }
    });
  }

  changeNumber(): void {
    this.router.navigate(['/recharge']);
  }

  priceLabel(amount: number, currency: string): string {
    const symbol = currency === 'INR' ? '₹' : `${currency} `;
    return `${symbol} ${amount}`;
  }

  viewDetails(pack: PlanSummary, event: Event): void {
    event.preventDefault();
    this.router.navigate(['/recharge'], {
      queryParams: { planId: pack.id, mobile: this.rawMobile }
    });
  }
}
