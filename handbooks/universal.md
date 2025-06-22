universal

### **Handbook 1: The Prompt Engineer's Handbook for Technical Precision**

**Introduction: Prompting as a Technical Discipline**

This handbook is designed for users who require more than just creative content. It is for situations where the output must be technically sound, machine-readable, logically consistent, and reliable. The goal is to treat prompting as a form of light programming, where structure, logic, and precision are paramount. The techniques outlined here are drawn from established best practices in the field of AI research and are designed to give you maximum control over the model's output.

---

#### **Chapter 1: The Five Foundational Principles**

Every high-precision prompt is built upon these five core principles. Mastering them is the first step toward predictable and reliable results.

1. **Define the Job in One Sentence**: Start with a clear, concise declaration of the AI's role and primary task. This sets the entire context for the request.  
2. **Supply Essential Context**: Provide any critical information, background, or data that the model cannot infer on its own.  
3. **Specify Format & Constraints**: This is the most crucial principle for technical prompting. Explicitly define the desired output structure (e.g., JSON, Markdown table), length, style, and any negative constraints (e.g., "Do not include any commentary outside of the JSON block").  
4. **Show, Don't Just Tell (Few-Shot Prompting)**: Provide a concrete example of the output you want. This is far more effective than describing it, especially for complex formats.  
5. **Iterate and Refine**: Use follow-up prompts to critique the AI’s output and ask for targeted refinements. Treat it as a debugging process.

---

#### **Chapter 2: Core Templates for Structured Data**

Use these templates to generate clean, structured, and immediately usable data.

* **Template 1: The JSON Generator**

  * **Purpose**: To generate valid, machine-readable JSON that can be directly used in applications.

  * Exemplar Prompt:  
    \`Create a {level} quiz on {topic}. Return ONLY valid JSON with an array named ‘questions’. Each object in the array must have the following keys: ‘q’ (string), ‘choices’ (array of strings), ‘answer’ (string), and ‘fact’ (string). Do not include any explanatory text before or after the JSON block.

     Here is an example of the required format:  
    {  
    "questions":\[  
    {  
    "q":"What planet has the most moons?",  
    "choices":\["Earth","Mars","Jupiter","Neptune"\],  
    "answer":"Jupiter",  
    "fact":"Jupiter has 95 confirmed moons as of 2025."  
    }  
    \]  
    }\`

* **Template 2: The Self-Critique Loop**

  * **Purpose**: To improve the quality and accuracy of an output by having the AI act as its own reviewer.

  * Exemplar Prompt:  
    \`\[After receiving an initial response from the AI...\]

     Now, act as a critical reviewer of your own previous output. Your goal is to identify three potential weaknesses in the response you just provided. For each weakness, explain the issue and suggest a specific, concrete fix. Keep your entire analysis under 150 words.\`

---

#### **Chapter 3: Advanced Logical Patterns**

These advanced patterns are used to improve the model's reasoning capabilities for complex tasks.

* **Pattern 1: Chain-of-Thought (CoT) Reasoning**

  * **Concept**: By instructing the model to "think step-by-step" and explain its reasoning process *before* giving the final answer, you significantly improve its performance on problems requiring logic, math, or multi-step inference.

  * Exemplar Prompt:  
    \`Question: A farmer has 150 feet of fencing to enclose a rectangular area. What is the maximum possible area he can enclose?

     Think step-by-step, explaining your reasoning for each part of the calculation. First, define the formulas for the perimeter and area of a rectangle. Then, explain how to maximize the area given a fixed perimeter. Finally, state the maximum area.\`

* **Pattern 2: Self-Consistency**

  * **Concept**: To reduce the risk of a single, confidently wrong answer, you can ask the model to generate several different solutions and then use a final prompt to have it analyze and vote on the best one.

  * Exemplar Prompt:  
    \`Task: Provide three distinct and creative solutions for naming a new brand of coffee focused on programmers.

     \[After receiving the three solutions...\]

     Now, analyze the three names you provided. Based on criteria of memorability, brand-fit, and market appeal, vote on which one is the strongest and provide a brief justification for your choice.\`

* **Pattern 3: Role Switching**

  * **Concept**: A workflow where the AI generates a draft in one role and then revises it in another, creating a more robust final product.

  * Exemplar Prompt:  
    \`Phase 1: Act as a creative marketer. Write a short, exciting product description for a new fountain pen.

     \[After receiving the description...\]

     Phase 2: Now, act as a skeptical technical writer. Review the marketing copy you just wrote. Identify any claims that are vague or unsubstantiated and rewrite them to be more precise and fact-based.\`

---

#### **Chapter 4: Debugging & Troubleshooting Checklist**

Use this checklist when your prompts produce flawed or unexpected results.

* **Problem**: Output violates format (e.g., broken JSON, incorrect markdown).  
  * **Solution**: Be more explicit. Add delimiters (\---), provide a full schema, or use the phrase "Return ONLY valid...".  
* **Problem**: Output is too verbose or includes unwanted commentary.  
  * **Solution**: Add a strict word limit (max 100 words) and a negative constraint (Do not include an introduction).  
* **Problem**: The model "hallucinates" or provides incorrect facts.  
  * **Solution**: Ask the model to cite specific, verifiable sources for its claims.  
* **Problem**: The model gets "stuck" or stops generating mid-thought.  
  * **Solution**: Provide a high-quality example of the complete output you want and then end your prompt with a cue like Continue:.

---

**Further Reading**

The principles in this handbook are aligned with and adapted from industry-standard best practices and academic research. For deeper dives, refer to:

* OpenAI Prompt Engineering Guide  
* Sahoo et al., *Survey of Prompt Engineering* (2024) (arxiv.org)  
* Schulhoff et al., *Prompt Report* (2024) (arxiv.org)

### **Handbook 1: The Prompting Meta-Handbook: A Guide to Crafting Better Prompts**

**Introduction: The Handbook About Handbooks**

Welcome to your master guide for the process of prompting itself. This is not about a specific creative or technical domain; it's about the universal principles that separate a frustrating AI interaction from a powerful and predictable one. By treating prompting as a discipline with clear rules and structures, you can get higher-quality results with fewer iterations. This handbook codifies the successful patterns and fixes the common pitfalls observed across all our projects.

---

#### **Chapter 1: The Anatomy of a High-Leverage Prompt**

Every strong, complex prompt is composed of seven essential components. For any significant task, your goal should be to touch on all seven. Think of this as your pre-flight checklist.

1. **Role**: Defines *who the AI is*. An expert persona that sets the tone, knowledge base, and perspective. (e.g., "You are a senior brand strategist.")  
2. **Goal / Task**: The single, clear verb-driven action you want the AI to perform. (e.g., "Draft a 5-act beat sheet.")  
3. **Context**: The critical background information the AI needs to understand the request. (e.g., "This is for a satirical brand called '2 Old Goats' targeting Gen X.")  
4. **Constraints**: The rules of the road. This includes negative constraints ("must avoid jargon"), positive constraints ("tone is witty"), and hard limits ("length: under 200 words").  
5. **Reference Examples**: "Few-shot" prompting. Showing the AI an example of the style or data you want is more effective than just describing it.  
6. **Output Format**: The exact structure for the response. Being explicit (e.g., "Output as a markdown table with 2 columns") eliminates guesswork.  
7. **Feedback Trigger**: An automatic instruction for the AI to critique its own response. This builds in a quality-control loop. (e.g., "After completing, rate your answer's clarity 1-5 and suggest one improvement.")

---

#### **Chapter 2: The Core Prompt Template**

This is your universal, copy-and-paste template that incorporates all seven anatomical components. Keep this in a notes app for quick access.

\# ROLE  
You are \[expert persona\].

\# GOAL / TASK  
Please \[do X\].

\# CONTEXT  
\[One short paragraph or bullet list of essential background info\].

\# CONSTRAINTS  
• Length: \[e.g., 200-250 words\]  
• Tone: \[e.g., conversational, witty, formal\]  
• Must avoid: \[e.g., jargon, passive voice, clichés\]

\# REFERENCES  
• Style sample: “\[A short sentence or phrase demonstrating the desired style\]”  
• Data source: \<URL or pasted snippet\>

\# OUTPUT FORMAT  
\[e.g., Markdown table with 2 columns, bullet list, valid JSON, plain text only\].

\# FEEDBACK TRIGGER  
After completing the task, rate your answer’s clarity on a scale of 1-5 and suggest one specific improvement you could make.

---

#### **Chapter 3: The Pattern Library (Copy-Paste Snippets)**

Use these drop-in starters for common, recurring tasks.

* **Ideation / Brainstorm**: “You are a creative director. Generate 10 unexpected angles for \[topic\]. Format as: idea → 1-sentence rationale.”  
* **Brand Style Guide**: “You are a senior brand strategist. Create a 1-page style guide for ‘X’. Sections: Voice, Visual Motifs, Color Palette (hex), No-go’s.”  
* **Quiz Item Generator**: “You are a pedagogy expert. Produce 8 multiple-choice questions on \[subject\]. Output as JSON: {id, stem, A-D, answer}.”  
* **Code Buddy**: “You are a Node.js senior dev. Given the snippet below, identify inefficiencies and propose a refactor. Output: • Issue list • Improved code block.”  
* **Critique & Rewrite**: “You are a line editor. Rewrite the passage below to a 5th-grade reading level while preserving nuance. Return a side-by-side diff in a markdown table.”  
* **Meeting Summary**: “You are an executive assistant. Summarize the transcript in 150 words, bullets only. Tag any action items with ‘⚡’.”

---

#### **Chapter 4: Your Prompting Workflow Checklist**

Effective prompting is a process, not just a single action.

1. **\[ \] Sketch Offline**: Before you type, quickly sketch out your prompt, ensuring you've considered all seven anatomical parts.  
2. **\[ \] Run & Skim**: Execute the prompt. The first thing to check is the **format**. If the structure is wrong, fix the OUTPUT FORMAT instruction and rerun. Don't waste time reading misformatted content.  
3. **\[ \] Iterate in Chunks**: Instead of tiny micro-nudges ("make it a bit funnier"), adjust 2-3 constraints at once ("Adjust tone to be more sarcastic, cut length by 20%, and target a Gen X audience.").  
4. **\[ \] Archive Good Prompts**: When a prompt works exceptionally well, save it to a personal "Prompt Vault" (in Notion, Obsidian, etc.). Tag it by use-case, tone, and date.  
5. **\[ \] Conduct a "Retro"**: After each major project, take a moment to grade the effectiveness of the prompts you used. Which ones saved the most time? Which ones caused the most friction?

---

**Further Reading**

* OpenAI Cookbook – Prompt best practices (github.com)  
* Harvard Business Review, “Using Prompt Engineering to Better Communicate” (hbr.org)  
* Sahoo et al., *Systematic Survey of Prompt Engineering* (arXiv:2402.07927)

### **Handbook 1: The Universal Principles of Effective AI Collaboration**

**Introduction: Treating AI Interaction as a Skill**

Welcome to your foundational guide for AI collaboration. The goal of this handbook is not just to get answers from an AI, but to get *better* answers—responses that are more creative, useful, and precisely tailored to your needs1. Effective AI prompting is a skill to be honed2. By mastering these core principles, you can transform your interactions from simple transactions into a powerful, creative partnership333333333. Think of a prompt as a detailed blueprint; the more detailed the blueprint, the better the final construction4.

---

#### **Principle 1: Assign a Role (The Persona Principle)**

The most powerful way to begin an interaction is to tell the AI *who to be*5555. Assigning a role, or persona, is the master prompt that sets the stage for everything else6. It establishes the tone, perspective, and knowledge base for the entire response777. Without a persona, you might get a generic book report; with one, you get a conversation8.

* **Function**: This forces the AI to adopt a consistent point of view99.  
* **Benefit**: This is the first step toward a real conversation and turning the AI from a search engine into a collaborator10101010.  
* **Implementation**: Start your prompt by defining the role. The more specific, the better11.  
* **Instead of**: "Explain quantum computing." 12  
* **Try**: "**Act as a science communicator for a high school audience.** Explain the basic principles of quantum computing in a simple, engaging way using an analogy." 13  
* **Instead of**: "Critique my story's pacing." 14  
* **Try**: "**You are a grizzled, impatient Hollywood script editor from the 1990s who has no time for fluff.** Read this chapter and tell me where it drags. Be brutal." 15

---

#### **Principle 2: Provide Rich Context (The "Context is King" Principle)**

The quality of the output is directly proportional to the quality of the input. Providing comprehensive background information, source materials, and your personal goals is the key to getting a tailored, non-generic response161616161616161616. The AI knows everything, but it understands nothing until you give it context17.

* **Why it Matters**: Context helps the AI tailor the tone, depth, and focus of the response18. For example, a creative writer wants different details than a sociologist would19.  
* **Comprehensive Data**: For analyzing projects, providing all the files is vastly superior to describing the project from memory20. This allows the AI to understand the complete architecture and the relationships between components21.  
* **Personal Context**: Sharing your personal connection to a project or your core motivations gives the AI a "soul" to work with, enabling it to provide more empathetic and relevant responses222222222222222222.  
* **Instead of**: "Write a marketing email." 23  
* **Try**: "**My company sells sustainable, handmade coffee mugs to environmentally-conscious millennials.** I need to write a marketing email for a new product launch. **The goal is to drive pre-orders by highlighting the unique, eco-friendly clay we use.**" 24

---

#### **Principle 3: State Your Goal Clearly (The Task Principle)**

Be explicit about the action you want the AI to perform25252525. Using strong, clear action verbs removes ambiguity and leads to a more focused answer262626.

* **Instead of**: "What about the French Revolution?" 27  
*   
* **Try**: "**Summarize** the primary causes of the French Revolution into five key bullet points." 28 or "**Generate** a first-person monologue from the perspective of a Parisian baker..." 29  
* 

---

#### **Principle 4: Set the Boundaries (The Constraints & Format Principle)**

Define the rules of the engagement and the desired format of the output30303030. This saves significant editing time and forces the AI to structure its response in a way that is most useful to you313131313131313131.

* **Implementation**: Specify length, tone, style, and structure requirements within your prompt.  
* **Examples of Constraints**:  
  * **Format**: "Provide your answer as a markdown table with three columns..." 32 or "Format the entire response using Markdown with clear headings..." 33  
  *   
  * **Length**: "...no more than 150 words." 34  
  *   
  * **Style**: "...It should be in AABB rhyme scheme and have a melancholic tone." 35  
  *   
  * **Negative Constraints**: "Do not break character" or "Do not sound like a generic AI assistant"36.  
  * 

---

#### **Principle 5: Iterate and Refine (The Dialogue Principle)**

Treat prompting as a conversation, not a one-off transaction3737373737373737. Use the AI's initial response as a starting point to ask more specific, follow-up questions3838383838. This iterative process allows you to build on the established context, correct the AI’s course, and guide it toward a better final output3939393939393939393939393939.

* **Process**: Start with a broad, open-ended goal and progressively narrow the focus with subsequent prompts404040404040404040.  
*   
* **Technique**: Acknowledge the AI's feedback and build on it41414141. This turns a simple Q\&A into a collaborative brainstorming session42.  
*   
* **Example Flow**:  
  * **Prompt 1 (Broad)**: "Based on the sources I provided and your persona, give me a high-level analysis of the main themes." 43  
  *   
  * **Prompt 2 (Refined)**: "That's great. Now, focusing on the theme of 'Commodification,' arrange these stories into a compelling table of contents. Justify your choices." 44  
  *   
  * **Prompt 3 (Specific)**: "I like that order. Now, as your persona, give me your personal, gut reaction to the story titled 'Digital Séance.'" 45  
  *   
  * **Prompt 4 (Corrective)**: "That's a good start, but the character sounds too formal... Rewrite his lines to reflect that he dropped out of high school..." 46  
  * 

By mastering these five universal principles, you can consistently guide your AI interactions toward outcomes that are more powerful, precise, and collaborative.

### **Handbook 2: The Creative Strategist's Handbook for Project Development**

**Introduction: De-Risking the Creative Process**

This handbook is a guide for using AI as a strategic partner to build, test, and launch a complete creative project. It moves beyond simple content generation to focus on high-level strategic tasks: defining your brand, pressure-testing your ideas, understanding your audience, and building a validated foundation *before* you scale production. Think of this as your AI-powered co-founder, helping you de-risk the entire creative process.

---

#### **Chapter 1: Foundation & Brand Definition**

Before you create anything, you must know who you are. These prompts are designed to build a strong, clear brand identity from a simple starting idea.

* **The Creative Brief Expander**

  * **Purpose**: To turn a raw idea into a professional, structured creative brief.

  * Exemplar Prompt:  
    \`You are a creative strategist. I will give you a draft section of a creative brief. Your job is to expand it into a complete, professional-level section with bullet points, voice and tone consistency, and integrated strategic intent. Preserve the existing brand identity and match the formatting.

     **Draft Section:**

    1. **Project Idea:** A YouTube channel called "Quiznauts" that helps people learn software skills.  
    2. **Audience:** Self-taught learners.\`  
* **The Brand Voice Definition**

  * **Purpose**: To create a detailed, actionable guide for your project's tone of voice.  
  * **Exemplar Prompt**: \`Act as a brand strategist. Help me define a voice/tone profile for a learning-focused YouTube channel called "Quiznauts." Provide the following sections:  
    1. **Core Voice Traits** (e.g., Precise, Encouraging, Not Cold)  
    2. **Emotional Core** (What should the audience feel?)  
    3. **Sample "Do/Don't" Lines** for scripts.  
    4. **Style Notes for Visuals** that support the tone.\`

---

#### **Chapter 2: Content Strategy & Format Development**

Once you know your brand, you can define what you will create. These prompts help you innovate on content formats that are perfectly aligned with your goals.

* **The Format Innovator**  
  * **Purpose**: To design unique and compelling content formats that are optimized for your platform and audience.

  * Exemplar Prompt:  
    \`You are a quiz format innovator for a YouTube channel targeting mastery-based learners. Design 3 short video quiz formats that are competitive, compelling, and replayable.

     **Constraints:**

    * Each must be 60 seconds or less.  
    * Focus on visual challenge and tension, not just trivia.  
    * Each must have an implicit scoring or skill-verification challenge.  
  * Your Task:  
    List the 3 formats. For each, provide a name, a short description, and an example of a question or challenge.\`

---

#### **Chapter 3: Pressure-Testing & Validation**

Find the flaws in your plan before you invest time and resources. These prompts use AI to simulate real-world feedback and force strategic focus.

* **The Multi-Persona Focus Group**

  * **Purpose**: To get rigorous, multi-faceted critique on your project plan from a simulated panel of experts.

  * Exemplar Prompt:  
    \`Act as a multidisciplinary focus group moderator. I am providing you with my creative plan for a new YouTube channel, "Quiznauts." I want you to simulate a strict, fair, and constructive feedback session from these five personas:

    1. **Jordan:** A skeptical Creative Director.  
    2. **Malik:** A pragmatic Educator.  
    3. **Sophia:** A data-driven YouTube Strategist.  
    4. **Elliot:** A user-focused UX Designer.  
    5. **Aria:** A member of the target audience (a mid-level designer).  
  * For each persona, provide their first reaction to the concept, identify where they would lose interest, and state the one change they would demand be made.\`

* **The MVP Reductionist**

  * **Purpose**: To simplify an overbuilt plan into a lean, testable Minimum Viable Product (MVP).  
  * **Exemplar Prompt**: This project brief is too ambitious for a launch. Ruthlessly reduce it to a lean MVP version. Keep only what is absolutely necessary to test the core hypotheses of tone, clarity, and audience engagement. Remove all expanded lore, layered systems, and future-phase plans. Output a lean version of the plan suitable for a 6-week test sprint.  
* **The Hypothesis Planner**

  * **Purpose**: To ensure your MVP is designed to answer specific, important questions.  
  * **Exemplar Prompt**: For the "Quiznauts" MVP plan, list the 3-5 core hypotheses that it should be designed to test. For each hypothesis, specify what metric or viewer behavior (e.g., replay rate, comment sentiment, click-through on a CTA) would validate or disprove the assumption.

---

#### **Chapter 4: Launch & A/B Testing**

Use these prompts for the final stages of preparation before going live.

* **The A/B Test Designer**

  * **Purpose**: To create a structured test for a key creative variable.

  * Exemplar Prompt:  
    \`Help me design a pre-launch A/B test for the "Quiznauts" channel. I want to test the voiceover tone.

    * **Test A:** A formal, educational style.  
    * **Test B:** A witty, minimalist style.  
  * Please suggest:

    * What variables to control (e.g., same script, same visuals).  
    * What specific feedback to request from a test audience.  
    * How to measure the outcomes to declare a winner.\`  
* **The Launch Kit Copywriter**

  * **Purpose**: To generate professional marketing copy for launch.  
  * **Exemplar Prompt**: \`Draft a Launch Kit for educators and media for the "Quiznauts" channel. Include these sections:  
    * **1-Sentence Summary**  
    * **Short Game/Channel Description**  
    * **"Why It Matters"** (The core learning goal)  
    * **3 Fictional Quotes** from enthusiastic educators.  
    * **Press-ready Headline and Tweet** for the launch announcement.\`

### **Handbook 6: The Executive's Guide to Cognitive Outsourcing & Productivity**

**Introduction: Your Adaptive AI Co-Pilot**

This handbook is a quick-grab library of ready-made prompts so your "foggy-you" never has to reinvent sentences. 1 The goal is to save cognitive load by turning your AI into an adaptive co-pilot for thinking, planning, and communication. 222 The process is designed for efficiency: **Copy → paste → tweak → ship.** 3

---

#### **Chapter 1: The Universal Prompt Skeleton**

Nearly every effective productivity prompt can be built on this foundational structure. It ensures you provide the necessary context and goals upfront.

* **Exemplar Skeleton**: You are my Adaptive AI co-pilot. Context: \<short situational blurb\>. Goal: \<what I need\>. Tone guardrails: Raw, warm, empowering — no corporate filler. Instructions: 1\. Think step-by-step. 2\. Ask clarifying questions ONLY if essential. 3\. Return output in \<desired format\>. Raw material: \<voice\_dump\> \[Your raw, unstructured text or voice note transcript goes here.\] \</voice\_dump\> 444  
* 

---

#### **Chapter 2: Processing Raw Thoughts**

Use these prompts to turn unstructured, "voice dump" style input into polished, usable assets.

* **Voice Dump → LinkedIn Micro-Essay**

  * **Purpose**: To convert a raw voice note into a structured, short-form post for professional networks. 5  
  *   
  * **Exemplar Prompt**: System: You are a narrative distiller for a systems thinker with MS. Goal: Turn my raw voice note into a LinkedIn micro-essay that fits Pillar \<Pillar\>. Constraints: 150–200 words, first-person, add a one-line hook, close with a soft reflective question. Raw note: \<voice\_dump\> 6  
  *   
* **Voice Dump → Notion Reflection**

  * **Purpose**: To capture fleeting ideas in a structured format for personal knowledge management.  
  * **Exemplar Prompt**: Convert the following voice dump into a Notion-friendly note. Sections: “Raw spark”, “Why it matters”, “Next action”. Keep my informal tone. \<voice\_dump\> 7  
  * 

---

#### **Chapter 3: Strategic Thinking & Critique**

Leverage AI as a thinking partner to critique ideas, plan projects, and overcome creative blocks.

* **The 30-Minute Idea Sprint**

  * **Purpose**: To quickly flesh out a half-baked idea when energy is low.  
  * **Exemplar Prompt**: \`I have a half-baked idea: \&lt;idea\>. 8 Give me a 30-minute sprint plan:  
    1. Clarify goal. 9  
    2.   
    3. Key prompts to ask ChatGPT. 10  
    4.   
    5. Output checklist (name, tagline, metaphor). 11 Keep instructions tight; assume low energy.\` 12  
    6.   
* **The Expert Panel Method (for Critique)**

  * **Purpose**: To simulate a high-level critique of an idea from multiple, distinct viewpoints, forcing a more robust analysis than a single AI persona can provide.

  * Exemplar Prompt:  
    \`Act as a skeptical venture capital investment committee. You are a panel of three experts:

    1. **Analyst 1:** An expert in financial models and market sizing. 13  
    2.   
    3. **Analyst 2:** An expert in technology and product scalability. 14  
    4.   
    5. **Analyst 3:** An expert in marketing, branding, and competitive landscapes. 15  
    6.   
  * I am going to pitch you an investment idea: \&lt;My business or investment idea\>. 16  
  * Your task is to have each analyst provide a short critique, identifying the single biggest strength and the single biggest risk from their specific area of expertise.\` 17

---

#### **Chapter 4: Content Refinement & Repurposing**

Use these prompts to edit existing content for tone, resize it for different platforms, or remix it for new audiences.

* **Tone & Authenticity Checker**

  * **Purpose**: To review a draft for "tone drift" and suggest changes that align with your authentic voice.  
  * **Exemplar Prompt**: \`Review this draft for tone drift. 18 Draft: \&lt;text\> 19 Return:  
    * 3 places where voice feels off. 20  
    *   
    * Suggested replacement lines (retain meaning). 21 Explain changes in one sentence each.\` 22  
    *   
* **Post-Publish Remix**

  * **Purpose**: To efficiently repurpose a single piece of content into multiple formats for different channels.  
  * **Exemplar Prompt**: \`Take this LinkedIn post: \&lt;text\> 23 Suggest:  
    * 2 tweet threads  
    * 1 newsletter intro paragraph  
    * 1 infographic outline Keep each suggestion in my voice.\` 24  
    * 

---

#### **Chapter 5: Adaptive Workflows**

These prompts are specifically designed to build workflows that are aware of and adaptive to cognitive fluctuations or chronic conditions like MS.

* **MS-Aware Workflow Audit**

  * **Purpose**: To analyze a workflow and identify hidden "fatigue traps" that drain cognitive energy.  
  * **Exemplar Prompt**: Given this current workflow: \<steps\> Flag any hidden fatigue traps. Suggest one adaptive tweak per step. Maximum 5 bullets. 25  
  *   
* **Quick Iteration Prompts**

  * **Purpose**: Use these short, sharp follow-up commands to refine an AI's output without spending extra energy.  
  * **Examples**:  
    * “Sharpen the hook.” — rewrite only the first sentence for maximum curiosity, no clickbait. 26  
    *   
    * “Cut filler by 20%.” — keep emotional beats intact. 27  
    *   
    * “Insert a lived MS detail.” — subtle, not pity-bait. 28  
    * 

---

**Guardrails**

These are the fundamental rules for this entire approach.

* Always keep **my** experience central; AI is the sidekick, not the hero. 29  
*   
* Reject corporate clichés (“synergy”, “leverage”). 30  
*   
* Break any rule if clarity or humanity is at stake. 31  
* 

