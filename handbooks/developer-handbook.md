developer-handbook

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

### **Handbook 3: The Game Designer's Toolkit**

**Introduction: From Haphazard Idea to Playable Prototype**

Every game begins as a messy, brilliant, and often overwhelming idea. 1111 This handbook is a practical toolkit for turning that creative spark into a structured, playable game. By partnering with an AI, you can build a systematic process for yourself, using it to handle structuring, content generation, and polishing. 2 This guide provides a collection of optimized, copy-and-paste prompts designed to help you generate mechanics, create narrative content, and analyze the balance of your game.

---

#### **Chapter 1: Finding the Core and Building the Roadmap**

Before creating components, you need a clear plan. These prompts help you distill your core idea and create an actionable roadmap to overcome creative paralysis. 3

* **The Roadmap Builder**  
  * **Purpose**: To create a step-by-step project plan from a defined goal. 4  
  * Exemplar Prompt:  
    \`ROLE: You are a 'Project Manager' and 'Creative Coach.' 5

     TASK: I need a step-by-step roadmap to develop a creative project. My goal is to move from a feeling of being 'stuck' and 'haphazard' to a clear, actionable plan. 6 Based on the project description below, create a multi-phase roadmap (e.g., Phase 1: Foundation, Phase 2: Prototyping, etc.). 7 Each phase should contain 2-3 concrete, actionable steps with a brief explanation of "Why" each step is important. 8  
  * PROJECT DESCRIPTION:  
    \[Describe your project and your goal. For example, "I want to refine my nearly-complete game, 'Tuck'd-In Terrors,' into a polished, cohesive experience."\] 9\`

---

#### **Chapter 2: Generating Game Components & Mechanics**

Use these prompts to brainstorm and create new cards, mechanics, and scenarios that are consistent with your existing world. 10

* **Design a New Game Card**

  * **Purpose**: To generate a new, balanced card with a clear thematic concept and mechanics. 11111111  
  * Exemplar Prompt:  
    \`Act as a game designer for Tuck'd-In Terrors. Using the provided files for context, design a new Toy card. 12

    1. **Card Name**: The Raggedy Prince 13  
    2.   
    3. **Thematic Concept**: A once-noble doll that has been patched up so many times it has forgotten its own story. It protects other toys but falls apart in the process. 14  
    4.   
    5. **Desired Mechanics**: It should have a way to protect your First Memory (✧) and should involve a sacrifice (✂️) or exile component. 15  
    6.   
    7. **Target Mana Cost**: 3 16  
    8.   
    9. **Complexity**: Moderate 17  
    10.   
  * Please provide the following in a clear format: Card Name, Type & Icons, Cost, Quantity, Card Text, Flavor Text, and a brief Reasoning Note explaining its balance and theme. 18\`  
* **Brainstorm a New Keyword**

  * **Purpose**: To create and define a new keyword and understand its strategic purpose in the game. 191919  
  * Exemplar Prompt:  
    Act as a game mechanics designer. Based on the existing keywords inTuck'd-In Terrors\` (like Haunt, Echo), I want to brainstorm a new keyword. 20

    1. **Keyword Name Idea**: "Fray" 21  
    2.   
    3. **Thematic Idea**: Represents a memory or toy that is falling apart. The effect should be a small, recurring negative consequence. 22  
    4.   
  * Please provide:

    1. A clear rules definition for "Fray". 23  
    2.   
    3. An example of how it would look on a Toy card and a Ritual card. 24  
    4.   
    5. A short paragraph on what strategic purpose "Fray" would serve. 25\`  
    6. 

---

#### **Chapter 3: Narrative and World-Building**

Use these prompts to flesh out the story and emotional tone of your game, ensuring a consistent and immersive experience. 26

* **Generate Thematic Journal Prompts**

  * **Purpose**: To create new, tonally consistent narrative content for your game. 27272727  
  * Exemplar Prompt:  
    \`Act as a creative writer in the style of the 'memory journal prompts' file. My goal is to create a new Objective's worth of journal prompts. 28

    * **Objective Title**: "The Empty Swing Set" 29  
    *   
    * **Core Theme**: A memory of playing outside that is tinged with loneliness and the feeling of being watched. 30  
    *   
  * Please generate 12 new journal prompts, each 1-2 sentences long, that are evocative, slightly melancholic, and fit this theme. 31\`  
* **Write Rulebook Narrative in a Specific Voice**

  * **Purpose**: To seamlessly integrate new rules explanations into your existing narrative framework. 32  
  * Exemplar Prompt:  
    \`Using the persona of "The Rememberer" from the 'rulebook' file, write a new narrative section for the rulebook. 33

    * **Topic**: This section should introduce the concept of "Distortion" cards. 34  
    *   
    * **Tone**: It should be written in the same reflective, slightly unnerved voice. It should explain that as memories get deeper, they also become less reliable. 35  
    *   
    * **Desired Length**: 2-3 short paragraphs. 36\`  
    * 

---

#### **Chapter 4: Playtesting and Balance Analysis**

Use the AI as a dedicated playtest analyst to stress-test your ideas, find weak points, and clarify rules.

* **Request a Balance Analysis**

  * **Purpose**: To get targeted, constructive feedback on a specific game component you are concerned about. 37  
  * Exemplar Prompt:  
    \`Act as a playtest analyst. 38

    1. **Card to Analyze**: "The Whispering Doll" 39  
    2.   
    3. **My Concern**: I am concerned that the die roll result of (6) "Take an extra turn" is too powerful and creates a snowball effect. 40  
    4.   
  * Please provide a balance analysis.

    1. Confirm if my concern is valid. 41  
    2.   
    3. Suggest 1-2 specific, alternative effects for the \#6 die roll that are still exciting but more balanced. 42  
    4.   
    5. Provide the reasoning for your suggestions. 43\`  
    6.   
* **The Rule Clarification Loop**

  * **Purpose**: A simple but powerful technique to use during solo playtesting to resolve rules ambiguities quickly.  
  * **Process**:  
    1. **Ask a specific, small question**: "How many cards do I draw?" 44  
    2.   
    3. **Rephrase your understanding**: "So for the first night set up, I'm basically starting with two toys in play and I should have three cards in my hand?" 45 This allows the AI to pinpoint your exact misunderstanding and provide a precise correction. 46  
    4. 

### **Handbook 5: The Developer's Guide to Code & Project Analysis**

**Introduction: AI as a Specialized Technical Partner**

This handbook provides a set of principles and optimized prompts for leveraging an AI as a specialized assistant for software projects. The key to unlocking high-quality, relevant technical feedback is to move beyond simple questions and instead provide comprehensive context, assign expert personas, and demand structured output. By using these techniques, you can turn a general-purpose AI into an expert code reviewer, software architect, or QA engineer for your project.

---

#### **Chapter 1: The First Principle: Full Context is King**

For any technical analysis, the more relevant information you provide, the better the output. The single most effective thing you can do is provide the AI with the full context of your project.

* **Why it's Crucial**: Providing the complete project enables the AI to understand the complete architecture, see the relationships between modules (like how EffectEngine is used by TurnManager), and reference documents like ROADMAP.md and README.md111. This is vastly superior to pasting single files or describing the project from memory222222222.  
* 

---

#### **Chapter 2: High-Level Architectural Review**

Start with a big-picture understanding of the project's design, health, and progress.

* **Purpose**: To assess the overall architecture and how well the implementation aligns with the stated goals.

* Exemplar Prompt:  
  \`Act as a principal software architect3. Review the provided "TuckdInTerrors\_MonteCarloSim" project. Your goal is to assess the overall architecture and design4.

   Cross-reference the implemented modules with the project's stated goals in ROADMAP.md and README.md5.  
* Provide your review in a report format with these sections6:  
  1. **Architectural Strengths**: What design choices are particularly strong and scalable? 7  
  2.   
  3. **Potential Weaknesses**: What are the biggest architectural risks or potential future bottlenecks? 8  
  4.   
  5. **Roadmap Alignment**: How well does the current implementation align with the phases outlined in ROADMAP.md? 9\`  
  6. 

---

#### **Chapter 3: Code Quality and Refactoring**

Drill down into the code itself to identify areas for improvement, refactoring, and adherence to best practices.

* **Purpose**: To find specific "code smells," deviations from best practices, and opportunities to improve readability and maintainability10.  
* Exemplar Prompt:  
  \`Act as a senior Python developer who is an expert on clean code and PEP 8 standards11.

   Perform a code quality review of the entire src/tuck\_in\_terrors\_sim/ directory12. Your task is to identify "code smells," deviations from best practices, and opportunities for refactoring13.  
* Please format your output as a list of bullet points, grouped by filename14. For each point, provide the file and line number (if applicable), describe the issue, and suggest a specific improvement15.\`

---

#### **Chapter 4: Specific Module Deep-Dives**

"Zoom in" on the most complex or critical parts of your system to get an expert opinion on a specific implementation.

* **Purpose**: To analyze a critical module for scalability and get suggestions for alternative design patterns.

* Exemplar Prompt:  
  Act as a game engine developer. My main concern is thesrc/tuck\_in\_terrors\_sim/game\_logic/effect\_engine.py\` file. This module is critical and will become very complex16.

   Please analyze its current design, specifically the resolve\_effect\_logic, \_check\_conditions, and \_execute\_action methods17.  
* Provide answers to the following:

  1. What are the pros and cons of this design as more effects and conditions are added? 18  
  2.   
  3. Suggest an alternative design pattern (e.g., Command Pattern, Strategy Pattern) that might be more scalable19.  
  4.   
  5. Write a small code example of how the \_execute\_action for DRAW\_CARDS would look using your suggested pattern20.\`  
  6. 

---

#### **Chapter 5: Testing and Documentation**

Improve the project's robustness, ease of understanding, and long-term maintainability.

* **Purpose**: To identify gaps in testing and automatically generate high-quality documentation.

* Exemplar Prompt:  
  Act as a QA engineer with a focus on test automation and documentation. Review the project, focusing ontests/and the docstrings withinsrc/\`21.

  1. Analyze tests/game\_logic/test\_turn\_manager.py22. What are 2-3 critical edge cases that are currently not being tested? Provide them as a list23.  
  2.   
  3. The file src/tuck\_in\_terrors\_sim/game\_logic/turn\_manager.py is missing docstrings24. Please generate complete, Google-style docstrings for the \_begin\_turn\_phase and execute\_full\_turn methods25.\`  
  4. 

