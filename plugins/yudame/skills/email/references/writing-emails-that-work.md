# Writing Emails That Work

Nov 9, 2026 · @Tom Counsell

A good work email gives the answer first, promises nothing that was not agreed, and asks for nothing that needs a meeting. This guide has six rules and a checklist. Use it for any email, chat message or reply you send to a client or partner.

The two most important rules are Rule 2 and Rule 3. Breaking them causes real problems: missed deadlines that were never agreed, and meetings that waste everyone's time. The other rules make an email faster to read.

## Rule 1: Lead with the answer

Put the most important thing in the first sentence. Many readers only read the first two lines.

- If they asked a question, the first sentence is the answer.
- If you need something from them, the first sentence says what you need and by when.
- If you are reporting a problem, the first sentence says what broke and who is affected.

The reason and the details come after. Do not repeat their email back to them before you answer it.

**Weak:** "Thanks for your message about the login issue. We have looked into it and after some investigation we found that the problem was caused by an expired certificate, which we have now replaced."

**Strong:** "Login works again. The cause was an expired certificate. We replaced it at 14:10 and added an alert for the next expiry."

## Rule 2: Never promise what nobody agreed to

A promise is any sentence that makes you, your team or the client responsible for doing something after the email is sent. The reader treats every promise as a commitment, even a polite one. Before you write a promise, check that the person who owns the work has already agreed to it.

Promises are hard to see in your own writing because they feel like politeness. Look for these:

| Type | Examples |
| --- | --- |
| Future actions | I'll, we will, let me, I'll follow up, I'll look into it, I'll keep you posted |
| Deadlines | by Friday, end of week, early next week, within 48 hours, shortly, ASAP |
| Offers | happy to, glad to, I can also, would you like me to, feel free to send me |
| Open availability | let me know if you need anything, reach out anytime |
| Committing other people | the team will, our engineer will handle it, the client will send |
| Soft plans | we plan to, we expect to, the goal is to have. Readers hear these as dates. |
| Scope or price | we can include that, no extra charge, that's covered |

For each promise you find, do one of these, in this order:

1. **Do it now.** If you can put the answer, the link, the number or the file in this email, put it in and delete the promise.
2. **Delete it.** Most promises add nothing. The email works without them.
3. **Ask first.** If the promise is really needed, ask the person who owns the work before you send. Do not guess a date for someone else.

These are fine without checking: a promise that was already agreed, written in plain words, and facts about the past or present ("the fix went live on Tuesday").

## Rule 3: Answer in writing. Do not push it to a call.

If someone asks a question in writing, answer it in writing. A call costs two calendars, delays the answer by days, and leaves no record. Offering a call often means the writer has not done the thinking yet.

Watch for: hop on a call, quick chat, find some time, set up a meeting, schedule a sync, touch base, walk you through it, discuss further, easier to explain live, a booking link, "we can cover this in Thursday's call".

What to do instead:

- **You know the answer:** write it. If it is long, use short numbered steps or a screenshot.
- **You are missing information:** ask the one specific question they can answer in writing.
- **The topic is sensitive** (bad news, a price, a mistake): write it plainly and carefully. That is the job, and a written record protects everyone.

The only exception is when the purpose of the email is to set up a meeting someone asked for. Then keep the meeting details, and still answer everything else in the email.

## Rule 4: Check every fact

Every number, date, name, price and status in your email must come from a source you can point to: a ticket, a dashboard, a contract, a message. If you cannot point to it, check it or remove it.

- Spell people's names and company names exactly as they write them.
- Write dates with the month name ("12 November", not "12/11"). Readers in different countries read 12/11 as different days.
- Give times with a time zone ("14:00 Bangkok time").
- Never include internal information in a client email: other clients' names, rates, revenue, or private team discussion.

## Rule 5: Use plain English for international readers

Many readers do not speak English as a first language, and many will use a translation tool. Plain English is faster for everyone, including native speakers.

- One idea per sentence. Keep sentences under about 20 words.
- Use common words: "use", not "utilize". "Start", not "commence".
- Use one name for one thing. If you call it "the staging server" once, do not call it "the test box" later.
- Avoid idioms. Translation tools break them.
- Avoid formal phrases that add nothing.
- Write "or" instead of a slash. "Android or iOS", not "Android/iOS".
- Prefer a plain verb to a phrasal verb when one exists: "cancel", not "call off".

| Instead of | Write |
| --- | --- |
| circle back, touch base | reply, talk |
| at your earliest convenience | by 12 November (or the real date) |
| please be advised that | (delete it) |
| moving forward | from now on |
| on the same page | agree |
| ballpark figure | estimate |
| drop the ball | miss |

## Rule 6: Cut the filler

Every sentence should give the reader information or ask them for something. Delete the rest.

- **Openings to delete:** "Hope this email finds you well", "Thanks for reaching out", "Great question", "Just following up", "As you mentioned".
- **Closings to delete:** "Let me know if you have any questions", "Don't hesitate to contact me", "Hope this helps". End on your last useful sentence, then your name.
- **Sales words to delete:** seamless, robust, cutting-edge, game-changer, excited to, thrilled. They make a factual email sound like an advert.
- **Calm tone:** use exclamation marks and emoji rarely or not at all in client email.
- **Asking someone to act:** say why, not only what. "Please fill in the form by Thursday so we can size the next sprint" works better than "Please fill in the form."
- **Length:** an email can be a few short paragraphs. A chat message should be a few lines. If it is longer, put the detail in a document and link it.

## Before and after

A client asked why the new release is slower on Android.

**Before:**

> Hi Sarah, hope you're well! Thanks so much for flagging this, great catch. We'll dig into the performance numbers and get back to you by Friday with a plan. Happy to hop on a quick call if it's easier to walk through live. Let me know if you need anything else!

Problems: no answer, a deadline nobody agreed to ("by Friday"), an offer of a call, and three lines of filler.

**After:**

> Sarah, the slowdown comes from the new image library. It loads full-size images on Android before resizing them. On a mid-range phone, the home screen now takes 2.8 seconds to load, against 1.1 seconds before the release.
>
> The fix is to request resized images from the server. Can your team confirm the image server supports a width parameter?
>
> Minh

The second version gives the cause and the numbers, and it replaces the call with one question Sarah can answer in writing. It makes no promise, because nobody has agreed a date for the fix yet.

## Checklist before you send

Read your draft once more and check each line. If you used AI to write the draft, check it twice: AI drafts add promises and call offers often.

1. The first sentence is the answer, the request, or the main point.
2. Every "I'll", "we will", deadline and offer was agreed by the person who owns the work, or it is deleted.
3. No sentence pushes the topic to a call or meeting.
4. Every number, date, name and price comes from a source you can point to.
5. Dates use month names, and times have a time zone.
6. Sentences are short, with no idioms and no slashes.
7. No filler at the start or the end.
8. If you ask someone to act, you say why.
9. No internal information goes to a client.
