import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface PlanSummary {
  id: number;
  name: string | null;
  plan_type: string;
  mobile_number: string | null;
  amount: number;
  currency: string;
  amount_payable: number;
  amount_payable_currency: string;
  pack_type: string;
  data: string;
  talktime: string | null;
  duration: string;
  benefit_names: string[];
}

export interface Benefit {
  id: number;
  name: string;
  validity: string;
  description: string;
}

export interface PlanDetail {
  id: number;
  name: string | null;
  plan_type: string;
  mobile_number: string | null;
  amount: number;
  currency: string;
  amount_payable: number;
  amount_payable_currency: string;
  pack_type: string;
  data: string;
  talktime: string | null;
  duration: string;
  benefits: Benefit[];
}

export interface ReviewNote {
  id: number;
  plan_amount: number;
  plan_name: string | null;
  data: string;
  duration: string;
  benefit_name: string;
  note: string;
}

@Injectable({ providedIn: 'root' })
export class PlansService {
  private readonly baseUrl = 'http://127.0.0.1:5000/api';

  constructor(private http: HttpClient) {}

  getPlans(): Observable<PlanSummary[]> {
    return this.http.get<PlanSummary[]>(`${this.baseUrl}/plans`);
  }

  getPlan(planId: number): Observable<PlanDetail> {
    return this.http.get<PlanDetail>(`${this.baseUrl}/plans/${planId}`);
  }

  getBenefitReviewNotes(benefitId: number): Observable<ReviewNote[]> {
    return this.http.get<ReviewNote[]>(`${this.baseUrl}/benefits/${benefitId}/review-notes`);
  }
}
