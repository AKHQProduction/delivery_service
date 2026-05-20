# Discount Rules and Applied Discounts

Status: accepted

We will model discounts with two tables: `discount_rules` for shop-managed
client and product discount settings, and `applied_discounts` for the discount
snapshot used or disabled on a specific order. This keeps editable future rules
separate from historical order facts while avoiding four near-duplicate tables
for client rules, product rules, order discounts, and order item discounts.

## Considered Options

- Four specialized tables: `client_discount_rules`,
  `product_discount_rules`, `order_discounts`, and
  `order_item_discounts`.
- Two generic tables: `discount_rules` and `applied_discounts`.
- One combined table for both rules and order snapshots.

## Decision

Use two generic tables. `discount_rules` distinguishes client and product rules
with a target type and strict database constraints. `applied_discounts`
distinguishes order-level and order-item-level snapshots with a target type,
nullable order item reference, copied unit/value/minimum quantity fields, and
the calculated discount amount.

## Consequences

Discount settings can change without rewriting historical orders. Future orders
that already have snapshots keep them unless a manager explicitly recalculates
future orders from today or tomorrow as part of the rule change. The schema must
rely on clear check constraints and partial unique indexes so the generic tables
cannot represent invalid combinations such as a client rule with a minimum
quantity or two active product rules for the same quantity threshold.
