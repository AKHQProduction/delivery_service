# Context

## Order intake

Order intake is the domain path that turns a client, delivery slot, address,
phone, product list, payment method, and comment into a persisted Order.

It owns current Order creation policies: address and phone snapshots, product
name and price snapshots, optional recurring order link, balance payment,
missing-coordinate geocoding, and route insertion.

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
