# Context

## Order intake

Order intake is the domain path that turns a client, delivery slot, address,
phone, product list, payment method, and comment into a persisted Order.

It owns current Order creation policies: address and phone snapshots, product
name and price snapshots, optional recurring order link, balance payment,
missing-coordinate geocoding, and route insertion.

## Order Discount

An Order Discount is a client-specific reduction applied once to the whole
Order total.

A client can have at most one active personal Discount Rule.

A client personal Discount Rule is always available for that client's Orders
until the rule is changed or removed.

Client personal Discount Rules are managed from the client context.
Client lists and client detail views show compact personal discount indicators.

A fixed amount client Discount Rule reduces the Order total once, while a
percent client Discount Rule is calculated against the Order total after Order
Item Discounts.

## Order Item Discount

An Order Item Discount is a product-specific reduction applied to one Order
Item before the Order total is calculated.

Product-specific discounts become available after the Order Item quantity
reaches the configured minimum quantity.

When an Order Item reaches the minimum quantity, a fixed amount discount
reduces that Order Item subtotal once, while a percent discount is calculated
against that Order Item subtotal.

An Order Item Discount cannot reduce its Order Item total below zero.

A product cannot have two active Discount Rules with the same minimum quantity.

When several product Discount Rules are available for one Order Item, the
applied rule is the rule with the highest minimum quantity that the Order Item
reaches.

Product Discount Rules are managed from the product context.
Product lists show a compact discount indicator, while product detail and edit
flows show the discount quantity thresholds.

Managers who can manage clients, products, or orders can manage the related
Discount Rules and disable Applied Discounts on those Orders.

## Discount stacking

Discount stacking is the rule that Order Item Discounts are applied before the
Order Discount, and the final Order total cannot be less than zero.

An Order with a final total of zero is valid.

## Order total breakdown

An Order total breakdown is the split between the pre-discount item subtotal,
Order Item Discount total, Order Discount total, and final Order total.

Payments use the final Order total after Applied Discounts.

Revenue reporting uses the final Order total after Applied Discounts, while
product revenue reflects product-specific discounts and does not distribute
Order Discounts across Order Items.

Discount monetary amounts and Order totals are expressed in whole hryvnias.

Percent discounts are calculated against the relevant line or order amount and
rounded to the nearest whole hryvnia with half values rounded up.

Delivery route views expose only the final Order total, not the discount
breakdown.

Order exports use final Order totals after Applied Discounts; detailed order
exports include the discount breakdown, while route-style exports may show only
the final total.

Managers see the discount breakdown while creating, editing, or viewing an
Order, while dense Order lists show only the final Order total.
Order intake modals show the discount breakdown next to the Order total as the
manager changes the client, items, or quantities.
Order intake modals do not show product Discount Rules whose minimum quantity
has not been reached.
Applied Order Item Discounts appear compactly on their Order Item rows and as
an aggregate in the Order total breakdown.
Order Item rows keep the original price visible and show discount amount and
discounted line total separately.
Historical Order views present Applied Discounts as Order facts without warning
that the source Discount Rule later changed or was deactivated.

Order statistics include total discount amount as a separate metric.

Manager-facing Order breakdowns show manager-disabled Applied Discounts as
disabled lines instead of hiding them.

Regular Order templates do not store Applied Discounts; generated Orders
snapshot the Discount Rules available when each generated Order is created.

When a Discount Rule changes, future Orders keep their existing Applied
Discounts unless a manager explicitly recalculates them from today or tomorrow.
The default future Order policy for Discount Rule changes is to keep existing
future Order snapshots.
Managers can preview affected future Order counts before choosing a future
Order recalculation policy for a Discount Rule change.

Deleting a Discount Rule follows the same future Order recalculation policy as
changing a Discount Rule.

Future Order recalculation preserves manager-disabled Applied Discounts instead
of re-enabling them automatically.

## Discount Rule

A Discount Rule is a shop-managed condition that makes a discount available for
future Orders or Order Items.

Discount Rules support two value units: percent of the relevant price and fixed
amount in hryvnias.

Discount Rules cover both client-specific and product-specific discounts.
Category-level discounts are outside the initial discount management scope.
Shop-wide discounts are outside the initial discount management scope.

Discount Rule values use whole numbers: percent values are between 1 and 100,
fixed amounts are positive whole hryvnias, and product minimum quantities are
positive whole units.

Removing a Discount Rule deactivates it instead of deleting its history.
Inactive Discount Rules do not prevent creating a new active Discount Rule for
the same client or product quantity threshold.
Bulk import and export of Discount Rules is outside the initial discount
management scope.
Discount Rules do not have validity date ranges in the initial scope; active
rules stay available until deactivated.

## Applied Discount

An Applied Discount is the snapshot of a Discount Rule that was actually used
or explicitly disabled on a specific Order.

Manager-disabled Applied Discounts are saved with zero applied amount and keep
the source rule details that were available at the time.

Manager-disabled Applied Discounts are removed from an Order when their source
rule no longer applies to the current client, items, or quantities.

An available Discount Rule is not saved as an Applied Discount when its
discount base is already zero.

Available Discount Rules are applied automatically during Order intake, while a
manager may disable an Applied Discount for that specific Order.
Managers can only enable or disable available Applied Discounts on an Order;
they do not edit discount values inside the Order.

Applied Discounts remain stable when Discount Rules change, but relevant
Applied Discounts are recalculated when a manager changes the Order client,
items, or quantities.

Repeat-order flows copy the previous Order's client, items, and quantities, but
Applied Discounts are recalculated from the currently available Discount Rules.

## Regular Order resource impact

Regular Order resource impact is the domain path that reacts when a resource
used by future regular orders is removed.

It owns current impact policies: pausing affected regular orders when a product
or time slot is deleted, and clearing removed time slot references so paused
regular orders can remain inspectable instead of being deleted by the database.

## Regular Order template integrity

Regular Order template integrity is the backend path that answers whether a
regular order template is currently usable for creating orders.

It owns current runnable checks: required client address, phone, delivery slot,
at least one item, existing resources, and same-shop ownership for the client,
delivery slot, and products. It is read-only: callers decide whether a failed
check becomes a business error, a pause, or a UI warning.

## Regular Order template write policy

Regular Order template write policy is the backend path that turns manager
input for a regular order template into validated template state.

It owns current write-time policies: schedule normalization, item quantity
validation, client address and phone ownership, delivery slot ownership,
payment method availability, product ownership, and applying the resulting
state to a template. It does not commit transactions and does not decide whether
future generated orders should be rebuilt.

## Regular Order lifecycle

Regular Order lifecycle is the backend path that changes an existing regular
order template after it has been created.

It owns current lifecycle policies: pausing a template, resuming a runnable
template, deleting a template, deleting future generated orders, and rebuilding
future generated orders from the current template. It does not commit
transactions; command handlers still own transaction completion.

## Regular Order management context

Regular Order management context is the backend access path for commands that
manage a regular order template.

It owns current management access policies: resolving the current manager,
rejecting users that cannot manage the shop, loading a template by id, loading a
template with items when the caller needs item data, and enforcing same-shop
ownership. It does not commit transactions and does not perform business
actions such as pause, delete, resume, or run.

## Generated Order lifecycle

Generated Order lifecycle is the domain path for orders created from a regular
order template after they already exist as normal orders.

It owns current lifecycle policies: cancelling the occurrence ledger when a
generated order is deleted, optionally pausing the source regular order in the
same operation, and deleting generated future orders through the same Order
deletion path so balance rollback and route cleanup stay consistent.

## Regular Order planning UI workflow

Regular Order planning UI workflow is the frontend path that coordinates manager
actions around regular order templates after the list and form state already
exist.

It owns current planning interaction policies: opening pause/delete dialogs,
asking whether future generated orders should be deleted, asking whether the
newly created template should generate from today or tomorrow, and passing the
selected policy flags to the API before refreshing planning data.
Template row actions are intentionally hidden behind a settings modal so the
planning list remains a compact scan surface.
The dedicated planning page is a two-column client/workspace layout; recent
orders are not a page column there.

## Regular Order planning form

Regular Order planning form is the frontend path that turns client defaults,
manager input, available products, delivery slots, and payment methods into a
regular order template payload.

It owns current form policies: defaulting to the client's primary address and
phone, keeping schedule input stable, supporting multiple product/quantity
items, applying a seed from a previous order, and exposing intent-level actions
to the planning screen instead of raw field mutation details.
Creation is presented as a modal flow rather than an inline list expansion.
On the planning page, that modal can seed the template from one of the client's
recent orders before the manager edits schedule, delivery, payment, and items.
The same modal is used for template settings; saving in settings mode updates
the existing template rather than creating a copy.

## Regular Order planning list item

Regular Order planning list item is the frontend display path for a regular
order template row or summary.

It owns current row display policies: schedule labels, status badges, delivery
slot labels, item counts, optional client details, optional address details, and
caller-provided actions.

## Client planning data

Client planning data is the frontend read path for loading planning information
shown from a Client context.

It owns current client-scoped read policies: loading regular order templates by
client id instead of client-name search, and loading recent orders by client
context for repeat-order and regular-order seed flows.

## Regular Order planning read

Regular Order planning read is the backend path that builds the list and detail
read models for managing regular order templates.

It owns current read policies: scoping rows to the current shop, applying
manager filters including client id, preserving deleted resource references as
nullable fields, and returning item counts and detail items without exposing
planning screens to the write gateway.

## Recurring Order scheduling clock

Recurring Order scheduling clock is the backend time boundary for regular order
automation.

It owns current calendar policies: using the Kyiv business date, generating the
manual/automatic run window, and defining the future-order cleanup cutoff as
tomorrow so today already assigned to routes is not touched.
