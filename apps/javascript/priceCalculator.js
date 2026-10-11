function isValidPrice(value) {
  return typeof value === "number" && Number.isFinite(value);
}

function roundMoney(value) {
  return Math.round(value * 100) / 100;
}

function calculatePriceSummary(originalPrice, currentPrice) {
  if (!isValidPrice(originalPrice) || !isValidPrice(currentPrice)) {
    throw new TypeError("Prices must be finite numbers.");
  }
  if (originalPrice <= 0 || currentPrice <= 0) {
    throw new RangeError("Prices must be greater than zero.");
  }

  const savings = roundMoney(originalPrice - currentPrice);

  // Equal prices, or current price higher than original: no discount.
  if (savings <= 0) {
    return { originalPrice, currentPrice, savings: 0, discountPercent: 0, hasDiscount: false };
  }

  const discountPercent = roundMoney(((originalPrice - currentPrice) / originalPrice) * 100);
  return { originalPrice, currentPrice, savings, discountPercent, hasDiscount: true };
}

module.exports = { calculatePriceSummary };
