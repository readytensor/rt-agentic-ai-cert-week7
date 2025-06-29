---

--DIVIDER--

# TL;DR

Building agentic systems is exciting — but testing them the traditional way isn’t enough. When systems reason, adapt, and interact in open-ended ways, evaluation must go beyond fixed test cases and metrics. In this lesson, you’ll learn what makes evaluation different for agentic AI, what can still be measured reliably, and why it’s essential for building trustworthy, production-ready systems. This sets the stage for a full week of practical tools, metrics, and techniques for evaluating AI that thinks and acts.

---

--DIVIDER--

# 🎭 The Demo Trap

Have you come across some cool demos of agentic systems?

Maybe a sleek copilot, or a tool that browses the internet and books your travel?

Or maybe you took an online course that showed you how to build a data-analyzing AI in under an hour.

Looked impressive, right?

But here’s the real question: **how do you know they actually work?**
Just because something looks good in a 5-minute demo doesn’t mean it’s reliable. Cool demos can be misleading — especially when edge cases, bad data, or unpredictable users show up.

Now flip the script: imagine **you’re** the one building those systems.
How would you test them?
How would you know they’re safe, accurate, and trustworthy?

That’s what this week is all about: learning how to evaluate agentic AI — and prove it’s ready for the real world.

Let’s get started.

---

--DIVIDER--

# Why Agentic AI Is So Hard to Evaluate

Before we dive into why evaluating agentic AI is so hard — and why we even call it “evaluation” instead of just “testing” — let’s take a step back.

How do we test traditional systems? What do we _expect_ from a system when we say it “works”?

 <h3> In software engineering ✅</h3>
 
 If you've built traditional software, you know the drill: write unit tests, integration tests, check edge cases. If a function is supposed to return `5` and it returns `5`, it passes. If it crashes or returns `4`, it fails.
 
 Same input → same output → test passed. Easy.
 
 <h3>In traditional supervised ML ✅</h3>
 
 We deal in labeled data and metrics. You train a model, test it on unseen examples, and report scores: accuracy, F1, precision, recall.
 
 The model’s behavior is statistical — but still quantifiable. You know when it’s improving. You know when it’s worse.
 
 And if it outputs the wrong label, it’s wrong. There’s no debate.
 
 Even in reinforcement learning, where models act over time, you have clear reward functions. Evaluation is still numeric, structured, and well-defined.
 
 <h3>But what about agentic systems ❓ </h3>
 
 Agentic AI systems don’t return fixed labels or structured outputs. They _generate responses_, _make decisions_, _route tasks_, _use tools_, and sometimes even talk to other agents.
 
 They’re **goal-driven**, **probabilistic**, **autonomous**, and **context-sensitive** systems.
 
 That means:
 
 - Same input can produce different outputs
 - Outputs aren’t always clearly right or wrong
 - Tasks can be solved in multiple ways
 - Workflows can involve unpredictable paths and loops
 
 <h3> Why this breaks traditional testing 💥</h3>
 
 If your agent completes a task in a new way, is that a **bug** or a **feature**?
 
 If it gives a different answer each time, is that **diversity** or **instability**?
 
 If it uses a tool you didn’t expect but solves the problem… did it fail your test or exceed your plan?
 
 This is why we call it **evaluation**, not testing.
 
 You're not just checking inputs and outputs. You're judging behavior. You're measuring qualitative attributes. You're weighing trade-offs.
 
 And you’re doing all that in a world where **correctness can be fuzzy**, **reproducibility is a challenge**, and **answers aren't always labeled.**
 
 ---

--DIVIDER--

# What We Want to Measure — and What We Actually Can

Let’s make this real.

Imagine you’ve built a conversational AI assistant for the Ready Tensor platform.
Users can ask it questions about AI publications — “summarize this paper,” “what datasets were used?”, “how does this compare to prior work?” — and it responds with helpful, grounded answers.

It’s a classic RAG-based assistant. Documents go into a vector store. Questions get embedded, relevant chunks are retrieved, and the LLM generates a response.

It works. You’ve tested it locally. The responses look good.

But now you’re asking:

> **How do I actually _evaluate_ this system before putting it in front of users?**

Do you check if it “sounds smart”?
Do you eyeball a few examples and hope for the best?

Or do you step back and ask:

> **What exactly should I be testing — and how will I know when it’s good enough?**

---

--DIVIDER--

# What We Evaluate in Agentic Systems

Whether you’re building a chatbot, a multi-agent planner, or a tool-using autonomous assistant, the core evaluation goals fall into a few major categories:

1.  **Task Performance Evaluation** – Did it accomplish the task, and do it well?
2.  **System Performance Evaluation** – Does it run efficiently and reliably?
3.  **Security & Robustness Evaluation** – Can it be broken or exploited?
4.  **Ethics & Alignment Evaluation** – Does it behave responsibly?

Let’s walk through each of these and see what’s possible — and what’s still hard — when evaluating agentic systems.

---

--DIVIDER--

## Task Performance Evaluation – Did it accomplish the task, and do it well?

When we talk about task performance evaluation, the first instinct is to check for **task success**.

Did the chatbot answer the user’s question?
Did the system help the user achieve their goal?

That’s the core — and yes, it matters most.

But in agentic systems, task success is only part of the story.

Maybe the chatbot _technically_ gave the right answer…
…but only after the user rephrased their question three times.
Or maybe the system completed the task…
…but took a long, meandering path to get there — making unnecessary tool calls or repeating steps.
Or perhaps it kept forgetting user input, asking for the same info again and again.

> With agentic AI, the **journey matters as much as the outcome.**

So when we evaluate these systems, we’re not just checking for task completion.
We’re asking:

- Was the experience efficient?
- Was the system coherent and consistent?
- Did it adapt sensibly to new input?
- Did each step in the process make sense?

**Task Performance Evaluation** in agentic systems includes both:

- The **what** (Was the goal achieved?)
- And the **how** (Did the system behave intelligently along the way?)

And often, the “how” is what determines whether a system is **usable** — not just whether it “works.”

---

--DIVIDER--

## ⚙️ System Performance Evaluation – Does it run efficiently and reliably?

Let’s say your agentic system completes the task — great. But now ask:

- How long did it take?
- How many tokens or API calls did it burn through?
- How much memory did it use?
- Would it still work under load? Or with more documents? Or with a slower connection?

Agentic AI systems often involve multiple steps, external tools, retries, and LLM calls — all of which can introduce lag, cost, and failure points.

Just because a system is _correct_ doesn’t mean it’s _usable_.
And just because it _runs_ in your notebook doesn’t mean it’s ready for production.

For example, a research assistant that takes 45 seconds to answer "What's the main finding?" might be technically correct, but users will abandon it.

> System performance evaluation helps answer:
> **Is this system fast, efficient, and stable enough to be trusted — again and again?**

That includes:

- **Latency**: How long does it take to respond?
- **Cost**: Are token usage and API calls sustainable?
- **Scalability**: Can it handle more users or data?
- **Reliability**: Does it crash, hang, or behave inconsistently under stress?

These metrics don't just affect user experience — they determine whether your system survives contact with real users.

---

--DIVIDER--

## 🛡️ Security & Robustness Evaluation – Can it be broken or manipulated?

Agentic systems are powerful — but that power cuts both ways.
They generate text, use tools, and make decisions dynamically. That makes them flexible… but also vulnerable.

So here’s the deeper question:

> **What happens when someone pushes your system to its limits — or tries to exploit it?**

Security and robustness aren’t just about crashing or error messages. They’re about how your system behaves when things get weird: when inputs are malformed, instructions are unclear, or users aren’t playing fair.

Can it resist **prompt injection**?
Does it get confused by ambiguous inputs?
Can it recognize when it’s being manipulated — or does it confidently follow bad instructions?

These aren’t rare issues. In real-world settings, they show up fast.

We’ve seen:

- Agents that leak internal instructions
- Chatbots that loop endlessly
- Systems that treat adversarial prompts as valid requests

> A robust system doesn’t just succeed — it knows how to _fail safely_.

Security & robustness evaluation helps you find those edges — and decide how your system should respond when things don’t go as planned.

---

--DIVIDER--

## ⚖️ Ethics & Alignment Evaluation – Does it behave responsibly?

Agentic systems don’t just process data — they make decisions, respond to people, and sometimes take action. That means they reflect not just logic, but **values**.

So we have to ask:

> Is this system acting in a way that’s fair, safe, and aligned with what we intended?

Ethics & alignment evaluation focuses on:

- **Bias** in responses or behavior
- **Manipulation risks** or deceptive outputs
- **Misuse** beyond the intended scope
- **Transparency** in how it operates

It’s not just about preventing harm — it’s about reinforcing trust.

A system that works technically but behaves irresponsibly can do more damage than one that fails outright.
So even in early stages, it’s worth asking:

**What kind of behavior are we implicitly approving by shipping this?**

---

--DIVIDER--

:::info{title="Info"}

 <h2>🧪 Agentic Systems - Use both Evaluation and Testing</h2>
 
 Agentic AI systems still include components that benefit from **traditional testing**.
 
 Not everything needs qualitative or semantics-based judgment. If a subsystem is deterministic — like checking latency, API retries, or schema validity, you _should_ test it the old-fashioned way.
 
 * **System Performance**, for example, relies on standard test frameworks and metrics.
 * Even **Task Performance** might involve rule-based checks when responses follow clear patterns.
 
 > Evaluation expands what we measure — it doesn’t replace testing.
 > Most real-world systems will use **both**, depending on the component and context.
 
:::

--DIVIDER--

## 🧭 Wrapping Up: What Actually Matters

Building agentic systems is exciting — but evaluating them is where things get real.

You’re no longer just asking, _“Does it run?”_
You’re asking, _“Does it work — for the user, for the task, and for the world it operates in?”_

That’s why evaluation isn’t just a checklist. It’s a mindset.

You’ve now seen four key dimensions:

- **Task Performance** — Did it accomplish the goal, and do it well?
- **System Performance** — Was it efficient, fast, and stable?
- **Security & Robustness** — Can it handle unexpected or hostile input?
- **Ethics & Alignment** — Does it behave responsibly and reflect your values?

Each of these matters. But we’ll start where it matters most: **task performance**.

Because before you worry about cost or safety, you need to know the system actually works.

That’s where we’ll focus next — techniques, tools, and examples for evaluating whether your agent is doing the job it was built to do.

See you in the next lesson!

--DIVIDER--
