# The Big Ideas Behind AI-Staff-HQ

AI-Staff-HQ started because it was too hard to do big projects with normal AI chats. This is not just a piece of software. It is a set of rules that turned my small tests into a real system. I am sharing it because the ideas inside are very useful. The main idea is simple: your AI helpers should be built exactly the way you want them. They should work just as hard as a real team of humans.

## Keep It Small and Simple

I chose to keep the start of this toolkit very small. I did not want to give you a messy library full of hundreds of random helpers. When you have too many things to start with, it gets confusing. People end up just copying things without thinking. By giving you only the most important pieces, you get to carefully pick what you add next. You have to decide what jobs are important to you. A small start forces you to make good choices. 

## Blank Forms Are Better Than Finished Examples

Finished examples look nice because all the work is done. But a finished example almost never matches exactly what *you* need to do. That is why we use blank forms (templates) instead. A template asks you to fill in the blanks. It makes you think hard about your real work, your rules, and your choices. Our templates are tools for thinking. They ask the right questions while leaving plenty of room for your own answers.

## Why We Use YAML Files

We build our helpers inside files called `YAML`. We use YAML because humans can read it easily, computers understand it, and it is easy to see what changed. A helper file is not just a note; it is a strict list of rules. YAML keeps everything very neat: who the helper is, how to wake them up, and what good work looks like. 

## Bring Your Own Helpers

AI-Staff-HQ expects you to build your own helpers. This is the best way to do things! If I gave you my exact set of helpers, you would get all of my weird rules and mistakes. Instead, this toolkit shows you *how* helpers work together and *how* they share notes. You fill the team with the helpers you actually need for your job. The final result feels perfect because you built it for yourself, not for someone else.

## The Active Roster and the Extra Library

I started with just five helpers. Then I grew the team too far, and a big roster got messy fast. Too many helpers made it hard to pick the right one, so I pulled the team back to a small, sharp default. Now the system works like this:

- **The Active Roster (12):** This is the team that runs by default. It's a small, high-signal group that covers most everyday jobs. It also powers the flagship Planning Swarm. The list lives in `config/specialist_roster.yaml`.
- **The Extra Library (56):** These are experimental helpers, kept for weird or special jobs. They still work, but you turn them on yourself. That keeps the default team focused.
- **Make Your Own:** This is still the best way! Copy the blank form, make it fit your job, and add it to the `staff/` folder only when it proves it deserves a spot on your team.

The whole library is 68 helpers, but you should rarely need more than the active 12 plus a few of your own. A small default forces good choices, which is the whole point.

## How Much Detail Do You Need?

Not every helper needs 200 lines of rules. The amount of detail matches how hard the job is:

- **Lots of Rules (200+ lines):** Bosses like the Chief of Staff need lots of rules. They manage big projects, so they need to know exactly how to check the work and fix mistakes.
- **Medium Rules (100–150 lines):** Artists or Planners need enough rules to know what to draw or write, but without getting bogged down in boring details.
- **Short Rules (50–100 lines):** Tech helpers just need simple, exact rules so they don't break the code.

When you build a new helper, match the size of their file to the size of their job. Too many rules make them weird; too few rules make them forget what to do.

## Keep the AI's Brain Focused

Every helper and plan is built to save space in the AI's memory window. Large language models are very smart, but they can only remember so much at once, and memory costs money. Our folders are built so you only load what you need for that exact chore. That is why we just say the helper's name instead of copying their whole file every single time. This discipline keeps the chats fast, saves money, and stops the AI from getting confused.

## My Personal System Shared With You

You are exploring the personal system I use every single day. When something changes here, it is because something broke during my real work, not because of a marketing goal. I am very honest about this. You deserve to know where things might be broken before you spend your time. Treat every file here as a peek into a living project, not a final shiny product.

## Putting the Ideas to Work

Keep these big ideas in your head when you build your own helpers. When you add a new helper, ask yourself if their rules make teamwork easier. When you use a blank form, think about which lists actually help you do better work. The goal is not to copy my exact layout; the goal is to learn the rules that make an AI team amazing.

If you use AI-Staff-HQ this way, your AI helpers will match *your* brain, not mine. You will get more done because you understand exactly how the system works. Most importantly, you will be able to change it whenever you want!
