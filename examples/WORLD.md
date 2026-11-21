# WORLD.md: SliceRun, a made-up pizza delivery app

This is an example. Copy it to the root of your own repo and replace the places with your app's features. Pick a world from what your product is about: food delivery becomes a city of kitchens and riders, a music app a concert hall, a banking app a vault and tellers.

Explain-backs use these places instead of file names, then give file:line.

| Place | What it is in the app | Code |
|---|---|---|
| Front Door | Menu and cart screens | `src/ui/menu/`, `src/ui/cart/` |
| Order Desk | Checks the cart and creates the order | `src/orders/createOrder.ts` |
| Cashier | Takes payment and handles refunds | `src/payments/` |
| Kitchen | Restaurant side: accepts, cooks, marks ready | `src/kitchen/` |
| Dispatch Tower | Picks a rider for each ready order | `src/dispatch/assignRider.ts` |
| Riders | Live location and delivery status | `src/riders/` |
| Bell | Push notifications to the customer | `src/notify/` |
| Ledger | Database of orders, users and riders | `src/db/` |

## House rules

1. Only the Dispatch Tower assigns riders. Nothing else writes `order.riderId` (`src/dispatch/assignRider.ts`).
2. The Cashier charges once per order, even if the request is retried (`src/payments/charge.ts`).
3. The Bell never rings between 22:00 and 07:00 local time unless the order is out for delivery (`src/notify/quietHours.ts`).
