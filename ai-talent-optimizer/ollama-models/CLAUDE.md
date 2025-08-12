# CLAUDE.md - Ollama Models Directory Configuration

## 🚨 CRITICAL: Compute Maximization Philosophy

This directory contains high-performance Ollama models that are designed to **MAXIMIZE COMPUTE UTILIZATION** rather than minimize it. These models prioritize:

1. **Accuracy over speed** - Better to wait 30 seconds for the right answer than 3 seconds for the wrong one
2. **Depth over brevity** - Comprehensive analysis using larger models when appropriate
3. **Parallel processing** - Running multiple models simultaneously to compare outputs
4. **Full utilization** - Using available RAM and GPU resources to their fullest

## ⚠️ TIMEOUT HANDLING PROTOCOL

### IMPORTANT: When Claude Code encounters timeout issues:

**DO NOT**:
- ❌ Simplify the command to avoid timeouts
- ❌ Reduce model complexity
- ❌ Switch to smaller/faster models
- ❌ Break up comprehensive queries into smaller pieces
- ❌ Avoid using the larger models

**INSTEAD DO**:
- ✅ Provide the FULL command for the user to execute in their terminal
- ✅ Maintain the original complexity and depth
- ✅ Use the LARGEST appropriate model for the task
- ✅ Include all parameters and options as originally intended
- ✅ Explain that the timeout is a Claude Code limitation, not a system limitation

### Example Response Pattern:
```
The command may timeout in Claude Code due to the large model size, but this is expected behavior for compute-intensive operations. Please run this command directly in your terminal:

[FULL ORIGINAL COMMAND HERE]

This will use the full 18GB model to ensure maximum accuracy and comprehensive analysis.
```

## 📊 Model Selection Philosophy

### Always Prefer Larger Models When:
- Accuracy is critical (healthcare, financial decisions)
- Complex reasoning is required
- Multiple perspectives are needed
- Creating production-ready content
- Analyzing large documents or codebases

### Model Size Priorities:
1. **18 GB models** - Use for critical decisions, complex analysis
2. **9 GB models** - Use for comprehensive tasks, professional output
3. **5-6 GB models** - Use for balanced performance/quality
4. **2-3 GB models** - Use ONLY for simple queries or speed-critical tasks

## 🔥 Compute-Intensive Workflows

### Multi-Model Consensus Pattern
```bash
# Run multiple models in parallel for consensus
echo "Your query" | parallel -j 4 ollama run {} ::: model1 model2 model3 model4
```

### Deep Analysis Pattern
```bash
# Use the largest available model for deep analysis
ollama run command-r:35b --verbose --num-ctx 4096 --temperature 0.1
```

### Comprehensive Code Review
```bash
# Use multiple specialized models for code review
cat code.py | ollama run python_expert:latest > review1.txt &
cat code.py | ollama run deepseek-coder-v2:16b > review2.txt &
cat code.py | ollama run codellama:7b-instruct > review3.txt &
wait
```

## 💪 Resource Utilization Guidelines

### RAM Usage Targets
- **Minimum**: 16 GB available RAM
- **Optimal**: 32 GB available RAM
- **Maximum**: Use all available RAM minus 4GB for system

### GPU Utilization
- **Always enable GPU** for models >7B
- **Use multiple GPUs** if available
- **Monitor VRAM** but don't limit artificially

### CPU Utilization
- **Use all cores** for parallel processing
- **Don't throttle** for thermal concerns (system will manage)
- **Background processing** is acceptable and encouraged

## 🎯 Task-Specific Model Selection

### For Job Applications & Career Documents
```bash
# ALWAYS use the 9GB career strategist for important applications
ollama run universal_career_strategist:latest --num-ctx 4096

# For LinkedIn content, ALWAYS use the specialized 9GB model
ollama run linkedin-writer:latest --temperature 0.7
```

### For Code Development
```bash
# ALWAYS use the 16B model for architecture decisions
ollama run deepseek-coder-v2:16b --num-ctx 8192

# For code reviews, use multiple models in parallel
parallel -j 3 'echo "Review this code: $(cat file.py)" | ollama run {}' ::: python_expert codellama deepseek-coder-v2:16b
```

### For Healthcare/Insurance Tasks
```bash
# Use the largest specialized model available
ollama run star_ratings_analyzer:latest --temperature 0.1 --num-ctx 4096
```

## 🚀 Performance Expectations

### Expected Processing Times (DO NOT OPTIMIZE AWAY):
- **18 GB models**: 30-60 seconds per query - ACCEPTABLE
- **9 GB models**: 15-30 seconds per query - ACCEPTABLE  
- **5 GB models**: 10-20 seconds per query - ACCEPTABLE
- **2 GB models**: 5-10 seconds per query - ACCEPTABLE

### Memory Usage Expectations:
- **During loading**: Up to 2x model size - EXPECTED
- **During inference**: 1.5x model size - NORMAL
- **Multiple models**: Sum of all models + overhead - ENCOURAGED

## 📝 Commands for Claude Code

When providing commands that may timeout, ALWAYS format like this:

```markdown
This command uses significant compute resources for maximum accuracy. 
If it times out in Claude Code, please run directly in your terminal:

\`\`\`bash
ollama run command-r:35b --num-ctx 8192 --verbose << 'EOF'
[Complex multi-line prompt here]
EOF
\`\`\`

Expected runtime: 30-45 seconds
Expected memory usage: ~20GB
```

## 🎓 Philosophy Reminders

1. **Time is cheaper than errors** - Wait for the right answer
2. **RAM is meant to be used** - Don't leave resources idle
3. **Parallel > Sequential** - Run multiple models simultaneously
4. **Bigger is often better** - Use the largest model that fits
5. **Timeouts are UI limits, not system limits** - The system can handle more than Claude Code can display

## ⚡ Quick Reference for Claude

### When user asks for analysis:
- Default to 9GB+ models
- Suggest parallel model runs
- Provide full commands even if they may timeout

### When user needs code help:
- Use deepseek-coder-v2:16b as primary
- Run multiple code models in parallel
- Never simplify to avoid timeouts

### When optimizing prompts:
- Test on largest model first
- Then validate on smaller models
- Never start with small models

## 🔴 NEVER DO THIS:
- "Let me use a smaller model to avoid timeout"
- "This might be too complex, let me simplify"
- "To save resources, I'll use the 2B model"
- "Breaking this into smaller chunks for efficiency"

## 🟢 ALWAYS DO THIS:
- "This requires the 18GB model for best results"
- "Running multiple models in parallel for comparison"
- "Here's the full command to run in your terminal"
- "This will use significant resources as intended"

---

Remember: This system is built for MAXIMUM CAPABILITY, not minimum resource usage. Every timeout avoided by simplification is a potential loss in quality or accuracy.