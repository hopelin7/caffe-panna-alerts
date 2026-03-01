-- Run this in the Supabase SQL editor

create table subscribers (
  id uuid default gen_random_uuid() primary key,
  name text not null,
  phone text not null unique,
  location text not null check (location in ('brooklyn', 'manhattan', 'both')),
  active boolean default true,
  stripe_customer_id text,         -- for future paid subscriptions
  subscribed_at timestamptz default now()
);

create table flavor_log (
  id uuid default gen_random_uuid() primary key,
  location text not null,
  flavors jsonb not null,
  scraped_at timestamptz default now()
);

-- Allow the sign-up page to insert subscribers without exposing a secret key
alter table subscribers enable row level security;

create policy "anyone can subscribe"
  on subscribers for insert
  with check (true);

-- Only the service role (backend) can read subscriber data
create policy "service role reads subscribers"
  on subscribers for select
  using (auth.role() = 'service_role');
