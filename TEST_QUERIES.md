# Hard Test Queries for AI Social Media Manager

## 🔥 Multi-Agent Sequential Workflows

1. **"Analyze my Instagram performance from last week, create 3 post ideas based on what's working, and schedule them for tomorrow at 9am, 2pm, and 6pm"**
   - Tests: Analytics → Strategy → Content → Publishing (4 agents)
   - Should route through all agents sequentially

2. **"Check my engagement rate, generate a reel script about fitness, create an image for it, then schedule for Monday 8pm"**
   - Tests: Analytics → Content (with image) → Publishing
   - Image generation + scheduling

3. **"What's my best performing content type, create similar content with emojis, and post it tomorrow morning"**
   - Tests: Analytics insights → Content creation → Publishing
   - Agent communication between analytics and content

## 💡 Content Creation Edge Cases

4. **"Create an Instagram caption about our new AI feature; energetic tone; audience: creators; include hashtags"**
   - Tests: Content agent with specific requirements
   - Should have emojis, no markdown, hashtags

5. **"Generate a carousel post with 5 slides about social media tips, make it fun and engaging"**
   - Tests: Complex content structure
   - Should handle multi-slide concept

6. **"Write a controversial post about AI replacing jobs but make it thought-provoking not offensive"**
   - Tests: Tone balancing, sensitive topics
   - Should be engaging but appropriate

## 📊 Analytics Deep Dives

7. **"What's my engagement rate compared to last month? Which posts got the most comments? Why?"**
   - Tests: Analytics agent with multiple questions
   - Should provide insights, not just numbers

8. **"Show me my worst performing posts and explain what went wrong"**
   - Tests: Negative analysis
   - Should be constructive, not just critical

9. **"Am I posting at the right times? What's the best schedule for my audience?"**
   - Tests: Strategic analytics
   - Should analyze posting patterns

## 🎯 Strategy Challenges

10. **"Create a 30-day content strategy for launching a SaaS product with limited budget"**
    - Tests: Complex strategic planning
    - Should be detailed and actionable

11. **"My engagement dropped 40% this month. What should I do?"**
    - Tests: Problem-solving strategy
    - Should analyze and provide solutions

12. **"Plan a viral campaign for Gen Z audience around sustainability"**
    - Tests: Trend awareness, audience targeting
    - Should be creative and data-driven

## ⚡ Scheduling Edge Cases

13. **"Schedule 5 posts for next week at optimal times based on my analytics"**
    - Tests: Analytics → Publishing integration
    - Should use actual performance data

14. **"Post this tomorrow at 12.47pm: 'Big announcement coming! 🚀'"**
    - Tests: Specific time parsing (12.47pm format)
    - Should handle decimal time format

15. **"Schedule a post for next Monday morning, another for Wednesday evening, and one for Friday afternoon"**
    - Tests: Multiple relative time parsing
    - Should handle vague times correctly

## 🎨 Image Generation Tests

16. **"Create an image of a futuristic city with flying cars and neon lights, then make a caption for it"**
    - Tests: Image generation + content creation
    - Should generate image URL and caption

17. **"Generate a minimalist logo concept for a tech startup called 'NeuralFlow'"**
    - Tests: Specific image requirements
    - Should handle design requests

18. **"Make an image of a sunset beach scene and write a motivational quote to go with it"**
    - Tests: Image + text coordination
    - Should be cohesive

## 🔄 Complex Multi-Step Workflows

19. **"Analyze what content performs best, create 10 similar posts, schedule them throughout next month at peak engagement times"**
    - Tests: Full pipeline with multiple outputs
    - Analytics → Strategy → Content (10x) → Publishing (10x)

20. **"Look at my competitor's strategy, create better content ideas, generate 3 posts with images, and schedule them strategically"**
    - Tests: Competitive analysis + execution
    - Should handle complex reasoning

## 🚨 Error Handling Tests

21. **"Schedule a post for yesterday at 5pm"** 
    - Tests: Invalid time handling
    - Should handle gracefully (schedule for today/tomorrow)

22. **"Create content about [intentionally vague request]"**
    - Tests: Unclear input handling
    - Should ask clarifying questions

23. **"Analyze my TikTok performance"**
    - Tests: Unsupported platform
    - Should explain limitations

## 🎭 Tone & Style Tests

24. **"Write a professional LinkedIn post about our company milestone"**
    - Tests: Platform-specific tone
    - Should be professional, not casual

25. **"Create a funny meme-style caption for a cat video"**
    - Tests: Humor and casual tone
    - Should be playful with emojis

26. **"Write an apology post for a product delay, empathetic but professional"**
    - Tests: Sensitive communication
    - Should balance tone appropriately

## 🔬 Agent Communication Tests

27. **"First tell me my top 3 posts, then create similar content, then schedule it"**
    - Tests: Explicit sequential workflow
    - Should pass data between agents

28. **"Based on my analytics, what content should I create next? Then create it."**
    - Tests: Strategy using analytics data
    - Should reference actual metrics

29. **"Create a post, but first check what's trending and what worked for me before"**
    - Tests: Multiple data sources
    - Should combine insights

## 💥 Stress Tests

30. **"Create 20 different post variations about coffee, each with unique angle and tone"**
    - Tests: High volume content generation
    - Should maintain quality and variety

---

## Expected Behaviors:

✅ **Emojis in all responses** - No markdown formatting
✅ **Natural conversational tone** - Not robotic
✅ **Sequential agent execution** - For multi-step queries
✅ **Data passing between agents** - Content uses analytics insights
✅ **Proper error handling** - Graceful failures with helpful messages
✅ **Time parsing accuracy** - Handles various time formats
✅ **Image generation** - Returns valid URLs
✅ **Concise responses** - Not overly verbose

## Red Flags to Watch For:

❌ Markdown formatting (**, ##, ###)
❌ "I'm having trouble accessing the AI" without showing data
❌ Generic responses without using actual Instagram data
❌ Failed sequential workflows (agents not communicating)
❌ Scheduling errors or wrong times
❌ Missing emojis
❌ Overly long, formal responses
