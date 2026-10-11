const test = require("node:test");
const assert = require("node:assert/strict");
const { calculatePriceSummary } = require("./priceCalculator");

test("normal discount", () => {
  const r = calculatePriceSummary(80000, 74490);
  assert.equal(r.savings, 5510);
  assert.equal(r.discountPercent, 6.89);
  assert.equal(r.hasDiscount, true);
});

test("equal prices give no discount", () => {
  const r = calculatePriceSummary(50000, 50000);
  assert.equal(r.savings, 0);
  assert.equal(r.discountPercent, 0);
  assert.equal(r.hasDiscount, false);
});

test("current price higher than original gives no discount", () => {
  const r = calculatePriceSummary(50000, 55000);
  assert.equal(r.savings, 0);
  assert.equal(r.hasDiscount, false);
});

test("money is rounded to 2 decimals", () => {
  const r = calculatePriceSummary(100, 33.333);
  assert.equal(r.savings, 66.67);
  assert.equal(r.discountPercent, 66.67);
});

test("zero and negative prices are rejected", () => {
  assert.throws(() => calculatePriceSummary(0, 100), RangeError);
  assert.throws(() => calculatePriceSummary(100, 0), RangeError);
  assert.throws(() => calculatePriceSummary(-5, 100), RangeError);
  assert.throws(() => calculatePriceSummary(100, -5), RangeError);
});

test("missing or invalid prices are rejected", () => {
  assert.throws(() => calculatePriceSummary(undefined, 100), TypeError);
  assert.throws(() => calculatePriceSummary(100, null), TypeError);
  assert.throws(() => calculatePriceSummary(NaN, 100), TypeError);
  assert.throws(() => calculatePriceSummary(100, Infinity), TypeError);
  assert.throws(() => calculatePriceSummary("100", 90), TypeError);
});
