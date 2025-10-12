# 🚀 The CLI Workflow: Your AI Workforce on the Command Line

This document provides a guide for developers and other technical users who want to interact with their AI workforce through a command-line interface (CLI) like the Gemini CLI, OpenAI's codec, or Claude's code.

## 🎯 Core Concept

The CLI workflow allows you to integrate your AI workforce into your existing development environment. You can use shell scripts to automate your interactions with your specialists, pipe the output of one specialist to another, and integrate your AI workforce with other command-line tools.

## 🗺️ Step-by-Step Guide

### **1. Set Up Your Environment**

Before you can start using your AI workforce on the command line, you need to set up your environment. This will typically involve:

- **Installing the CLI tool:** Follow the instructions for your chosen AI platform to install their CLI tool.
- **Authenticating:** You will need to authenticate with the AI platform to use their CLI tool. This will typically involve setting an environment variable with your API key.

### **2. Build Your Team**

As with the other workflows, the first step is to build your custom team of specialists. Use the `templates/persona/new-staff-member-template.md` to create your specialists, and use the `Prompt Engineer` to help you design their capabilities.

### **3. Craft Your Prompts**

When you are using the command line, you will typically pass your prompt to the CLI tool as a string. You can also use shell commands like `cat` to pass the content of a file as part of your prompt.

For example, to have the `Prompt Engineer` review a file called `my-script.py`, you could use a command like this:

```bash
cat my-script.py | gemini "Act as the Prompt Engineer from my AI-Staff-HQ. Please review this Python script and suggest improvements."
```

### **4. Activate Your Specialists**

You can activate your specialists using the same `Acting as the [ROLE]...` pattern as in the other workflows. The key is to provide the AI with the full context of your project by passing the relevant files as part of the prompt.

### **5. Chain Commands**

The real power of the CLI workflow comes from the ability to chain commands together. You can pipe the output of one specialist to another, or use shell scripts to create complex, automated workflows.

For example, you could create a script that:

1.  Uses the `Market Analyst` to research a topic.
2.  Pipes the `Market Analyst`'s research to your custom `Copywriter` specialist to write a blog post.
3.  Pipes the `Copywriter`'s blog post to your custom `SEO Specialist` to optimize it for search engines.

## 🌟 Benefits of the CLI Workflow

- **Automation:** You can automate your interactions with your AI workforce using shell scripts.
- **Integration:** You can integrate your AI workforce with other command-line tools.
- **Power:** The CLI workflow provides a powerful and flexible way to interact with your AI workforce.

This workflow is recommended for developers, technical users, and anyone who wants to automate their AI workflows.
