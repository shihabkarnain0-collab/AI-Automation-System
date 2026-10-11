const { calculatePriceSummary } = require("./priceCalculator");

const productPrice = 80000;
const discountPrice = 74490;
const summary = calculatePriceSummary(productPrice, discountPrice);

console.log("AI Automation System - Price Analysis");
console.log(`Original price: ৳${summary.originalPrice}`);
console.log(`Current price: ৳${summary.currentPrice}`);
console.log(`Customer saves: ৳${summary.savings}`);
console.log(`Discount: ${summary.discountPercent}%`);
