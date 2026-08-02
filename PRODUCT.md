# Product

## Register

brand

## Users

Ukrainians who left the country and now live abroad, mostly in Poland, Germany and Czechia.
Many are women, often with children; men of conscription age are a smaller and more
constrained segment. They are working, they have limited leave, and dental work in their
country of residence costs three to seven times what it costs at home.

Their context when they land on the page: they already suspect treatment back home is
cheaper, and they are trying to find out whether the saving survives the trip, and whether
the clinic is real. They arrive from a Warsaw ad or a price-related search, usually on a
phone, usually with a specific tooth in mind.

The job to be done: get a believable number for their own case, and a way to ask a question
without booking anything or giving up a phone number.

## Product Purpose

ONNO is an intermediary, not a clinic. It puts a patient in front of a partner dental clinic
in Lviv and takes care of everything around the treatment: first contact, an AI
pre-assessment from photos, the price, the transfer from Warsaw, the hotel.

The single action the page exists to produce is a Telegram conversation with the assistant.
Nothing is sold on the page and no form completes a purchase. Success is a message sent.

The partner clinic is deliberately never named. ONNO intends to add more clinics, so the
brand must carry the credibility that a named clinic would normally carry.

## Brand Personality

A good private clinic that happens to publish its prices. Competent, calm, direct.

The tension that defines the voice: the tone is clinical and trustworthy, but the first
question the page answers is "what does it cost". Those are not in conflict here, they are
the whole idea. **Publishing the number confidently is the trust move.** Clinics that hide
prices make people assume the worst; stating the figure plainly, explaining what is inside
it, and saying who confirms it, is what a serious operator does.

Three words: assured, plain-spoken, unhurried.

Not friendly-chatty, not luxurious, not clever. No exclamation marks, no urgency devices.

## Anti-references

- **The page as it stands.** A twelve-row price table with three columns of numbers, giant
  headings, oceans of whitespace, no offer, no call to action above the fold. It reads as a
  clinic's internal price list that someone published by accident.
- **Discount-shop patterns.** Red percentage badges, countdown timers, "limited places",
  crossed-out prices, star showers. In a medical service these destroy the credibility that
  the whole business depends on.
- Also avoid: cold corporate-hospital navy-and-stock-photography, and effect-heavy agency
  pages where motion outweighs content.

## Design Principles

1. **The number is the trust signal.** Lead with the price because stating it plainly is
   what a confident operator does, not because it is a bargain. Never dress it as a discount.
2. **Every claim carries its receipt.** The 4.8/98 rating is real and from a real profile;
   the before/after images are real cases; the country comparison cites its sources. If a
   claim has no receipt, cut the claim rather than soften it.
3. **Hide the clinic, show the competence.** The brand cannot lean on a clinic name, a
   street address or a Google Business listing. Credibility has to come from what is
   published: guarantees in writing, the timeline, the disclaimer, the sourced comparison.
4. **One action.** Every section ends in the same place: a message to the assistant. No
   secondary conversion, no newsletter, no form that competes with it.
5. **Machines are already served.** Structured data, llms.txt and the price pipeline are
   built and consistent. Work on this surface is for the human reading it, and no SEO
   argument justifies making the page worse to read.

## Accessibility & Inclusion

WCAG 2.1 AA. Body text at 4.5:1 minimum against its background; the existing muted grey on
tinted near-white is the known weak spot and must be checked, not assumed.

The audience is not young by default and often reads on a phone in a second or third
language. That means generous tap targets, real font sizes rather than elegant small type,
and no meaning that exists only in colour or only in motion.

Cyrillic coverage is a hard constraint on every typeface: the same page ships in Ukrainian,
Russian and English, and a font without Cyrillic silently breaks two of the three.

`prefers-reduced-motion` must have a real alternative for anything that animates. Content
must never be hidden behind a scroll-triggered reveal, because a headless renderer or a
background tab will ship it blank.
