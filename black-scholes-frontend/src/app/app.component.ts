import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  S = 100;
  K = 100;
  T = 1.0;
  r = 0.05;
  sigma = 0.2;
  price: number | null = null;
  loading = false;
  error: string | null = null;

  constructor() {}

  calculate() {
    this.error = null;
    this.loading = true;
    // Placeholder logic for calculation
    setTimeout(() => {
      this.price = Math.random() * 100; // Replace with API call logic
      this.loading = false;
    }, 1000);
  }
}
