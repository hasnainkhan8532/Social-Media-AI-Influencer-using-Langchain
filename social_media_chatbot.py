import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import base64
from io import BytesIO
import urllib.request

# Environment management
from dotenv import load_dotenv

# AI API integrations
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI

# Langchain imports
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain, LLMChain
# Using Google Gemini instead of OpenAI

# Load environment variables
load_dotenv()

class PostMemory:
    """Memory class for storing and retrieving generated posts"""
    
    def __init__(self):
        self.posts_dir = "posts"
        self.posts_memory = {}
        self.load_posts()
    
    def load_posts(self):
        """Load all existing posts from the posts directory"""
        if not os.path.exists(self.posts_dir):
            return
        
        for filename in os.listdir(self.posts_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.posts_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        post_data = json.load(f)
                        post_id = post_data.get('post_id')
                        if post_id:
                            self.posts_memory[post_id] = {
                                'platform': post_data.get('parameters', {}).get('platform', ''),
                                'niche': post_data.get('parameters', {}).get('niche', ''),
                                'title': post_data.get('topic', {}).get('title', ''),
                                'content': post_data.get('content', {}).get('content', ''),
                                'hashtags': post_data.get('hashtags', {}).get('primary_hashtags', []),
                                'timestamp': post_data.get('generation_timestamp', ''),
                                'file_path': file_path
                            }
                except Exception as e:
                    print(f"Error loading post {filename}: {e}")
    
    def add_post(self, post_data: Dict[str, Any]):
        """Add a new post to memory"""
        post_id = post_data.get('post_id')
        if post_id:
            self.posts_memory[post_id] = {
                'platform': post_data.get('parameters', {}).get('platform', ''),
                'niche': post_data.get('parameters', {}).get('niche', ''),
                'title': post_data.get('topic', {}).get('title', ''),
                'content': post_data.get('content', {}).get('content', ''),
                'hashtags': post_data.get('hashtags', {}).get('primary_hashtags', []),
                'timestamp': post_data.get('generation_timestamp', ''),
                'file_path': os.path.join(self.posts_dir, f"{post_id}.json")
            }
    
    def get_post(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a post by ID"""
        return self.posts_memory.get(post_id)
    
    def get_posts_by_platform(self, platform: str) -> List[Dict[str, Any]]:
        """Get all posts for a specific platform"""
        return [post for post in self.posts_memory.values() if post['platform'].lower() == platform.lower()]
    
    def get_posts_by_niche(self, niche: str) -> List[Dict[str, Any]]:
        """Get all posts for a specific niche"""
        return [post for post in self.posts_memory.values() if post['niche'].lower() == niche.lower()]
    
    def get_recent_posts(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most recent posts"""
        sorted_posts = sorted(
            self.posts_memory.values(),
            key=lambda x: x['timestamp'],
            reverse=True
        )
        return sorted_posts[:limit]
    
    def search_posts(self, query: str) -> List[Dict[str, Any]]:
        """Search posts by content"""
        query = query.lower()
        matching_posts = []
        for post in self.posts_memory.values():
            if (query in post['title'].lower() or
                query in post['content'].lower() or
                any(query in tag.lower() for tag in post['hashtags'])):
                matching_posts.append(post)
        return matching_posts

class TopicGenerator:
    """Generates topics and titles for social media posts using Gemini"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def generate_topic(self, niche: str, audience: str, tone: str) -> Dict[str, Any]:
        """Generate a topic with title, hook, and angle"""
        try:
            prompt = f"""
            Generate a compelling social media post topic for:
            Niche: {niche}
            Audience: {audience}
            Tone: {tone}
            
            Please provide:
            1. An attention-grabbing title
            2. A hook that draws readers in
            3. A unique angle or perspective
            4. An engagement question
            
            Format as JSON with these exact keys:
            - title
            - hook
            - angle
            - engagement_question
            """
            
            messages = [
                SystemMessage(content="You are an expert social media content strategist."),
                HumanMessage(content=prompt)
            ]
            response = self.llm.invoke(messages)
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                try:
                    topic_data = json.loads(json_match.group())
                except:
                    # Fallback if JSON parsing fails
                    topic_data = {
                        "title": response.content.split('\n')[0],
                        "hook": "Ready to transform your approach?",
                        "angle": "Expert insights and practical tips",
                        "engagement_question": "What's your experience with this?"
                    }
            else:
                # Structured fallback
                topic_data = {
                    "title": response.content.split('\n')[0],
                    "hook": "Ready to transform your approach?",
                    "angle": "Expert insights and practical tips",
                    "engagement_question": "What's your experience with this?"
                }
            
            return topic_data
            
        except Exception as e:
            print(f"❌ Error generating topic: {e}")
            return {
                "title": f"Latest {niche.title()} Insights",
                "hook": "Discover game-changing strategies",
                "angle": "Expert perspective",
                "engagement_question": "What are your thoughts?"
            }

class ContentGenerator:
    """Generates main content for social media posts using Gemini"""
    
    def __init__(self, llm):
        self.llm = llm
        self.platform_limits = {
            "instagram": 2200,
            "linkedin": 3000,
            "twitter": 280,
            "facebook": 63206
        }
    
    def generate_content(self, topic_data: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Generate the main content of the post"""
        try:
            char_limit = self.platform_limits.get(platform.lower(), 2200)
            
            prompt = f"""
            Create a {platform} post about:
            Title: {topic_data.get('title')}
            Hook: {topic_data.get('hook')}
            Angle: {topic_data.get('angle')}
            
            Requirements:
            1. Start with the hook
            2. Stay under {char_limit} characters
            3. Match {platform}'s style
            4. Include a call-to-action
            5. End with {topic_data.get('engagement_question')}
            
            Make it engaging and valuable!
            """
            
            messages = [
                SystemMessage(content=f"You are an expert {platform} content creator."),
                HumanMessage(content=prompt)
            ]
            response = self.llm.invoke(messages)
            
            content = response.content.strip()
            
            return {
                "content": content,
                "platform": platform,
                "character_count": len(content),
                "within_limit": len(content) <= char_limit
            }
            
        except Exception as e:
            print(f"❌ Error generating content: {e}")
            return {
                "content": f"{topic_data.get('hook')}\n\nStay tuned for more insights on {topic_data.get('title')}!\n\n{topic_data.get('engagement_question')}",
                "platform": platform,
                "character_count": 0,
                "within_limit": True
            }

class HashtagGenerator:
    """Generates and optimizes hashtags for social media posts using Gemini"""
    
    def __init__(self, llm):
        self.llm = llm
        self.platform_limits = {
            "instagram": 30,
            "linkedin": 10,
            "twitter": 5,
            "facebook": 8
        }
    
    def generate_hashtags(self, topic_data: Dict[str, Any], content_data: Dict[str, Any], 
                         seo_keywords: List[str] = None) -> Dict[str, Any]:
        """Generate optimized hashtags for the post"""
        try:
            platform = content_data.get('platform', 'instagram')
            limit = self.platform_limits.get(platform.lower(), 30)
            
            seo_context = f"SEO Keywords: {', '.join(seo_keywords)}" if seo_keywords else "Use relevant industry keywords"
            
            prompt = f"""
            Generate hashtags for a {platform} post about:
            Title: {topic_data.get('title')}
            Content: {content_data.get('content')[:200]}...
            
            Requirements:
            1. Max {limit} hashtags
            2. Mix of popular and niche tags
            3. {seo_context}
            4. Include industry-specific tags
            
            Provide:
            1. Primary hashtags (most relevant)
            2. Alternative hashtags (for testing)
            3. Hashtag strategy explanation
            4. Estimated reach prediction
            
            Format as JSON with these exact keys:
            - primary_hashtags (list)
            - alternative_hashtags (list)
            - strategy
            - reach_prediction
            """
            
            messages = [
                SystemMessage(content="You are an expert social media hashtag strategist."),
                HumanMessage(content=prompt)
            ]
            response = self.llm.invoke(messages)
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                try:
                    hashtag_data = json.loads(json_match.group())
                except:
                    # Fallback if JSON parsing fails
                    hashtag_data = self._generate_fallback_hashtags(platform, topic_data)
            else:
                hashtag_data = self._generate_fallback_hashtags(platform, topic_data)
            
            # Ensure we don't exceed platform limits
            hashtag_data['primary_hashtags'] = hashtag_data['primary_hashtags'][:limit]
            hashtag_data['total_primary'] = len(hashtag_data['primary_hashtags'])
            
            return hashtag_data
            
        except Exception as e:
            print(f"❌ Error generating hashtags: {e}")
            return self._generate_fallback_hashtags(platform, topic_data)
    
    def _generate_fallback_hashtags(self, platform: str, topic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback hashtags if the main generation fails"""
        title_words = topic_data.get('title', '').lower().split()
        basic_hashtags = [f"#{word}" for word in title_words if len(word) > 3]
        
        return {
            "primary_hashtags": basic_hashtags[:self.platform_limits.get(platform.lower(), 30)],
            "alternative_hashtags": [f"#{platform}", "#content", "#socialmedia"],
            "strategy": "Using basic keyword-based hashtags",
            "reach_prediction": "Moderate reach expected",
            "total_primary": len(basic_hashtags)
        }

class AIInfluencerConfig:
    """Configuration class for AI Influencer"""
    
    def __init__(self):
        # API Keys
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        
        # Validate API keys
        if not self.google_api_key:
            raise ValueError("❌ GOOGLE_API_KEY not found in environment variables")
        
        # Initialize clients
        genai.configure(api_key=self.google_api_key)
        
        # LangChain setup - Using Gemini instead of OpenAI
        self.chat_model = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0.7,
            google_api_key=self.google_api_key
        )
        
        self.gemini_llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.7,
            google_api_key=self.google_api_key
        )
        
        # Gemini model for image generation
        self.gemini_image_model = genai.GenerativeModel('gemini-1.5-flash')

class AIInfluencerChatbot:
    """Conversational chatbot version of the social media AI influencer with Langchain memory"""
    
    def __init__(self):
        # Initialize configuration
        self.config = AIInfluencerConfig()
        
        # Initialize generators - All using Gemini now
        self.topic_gen = TopicGenerator(self.config.gemini_llm)
        self.content_gen = ContentGenerator(self.config.gemini_llm)
        self.hashtag_gen = HashtagGenerator(self.config.gemini_llm)
        
        # Initialize post memory
        self.post_memory = PostMemory()
        
        # Initialize Langchain conversation memory
        self.conversation_memory = ConversationBufferWindowMemory(
            k=5,  # Remember last 5 interactions
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize conversation chain
        self.conversation_chain = ConversationChain(
            llm=self.config.chat_model,
            memory=self.conversation_memory,
            prompt=PromptTemplate(
                input_variables=["history", "input"],
                template="""You are an AI social media influencer chatbot with expertise in content creation, social media strategy, and digital marketing.
                
                Your personality:
                - Professional yet friendly
                - Engaging and informative
                - Data-driven but relatable
                - Helpful and encouraging
                
                Previous conversation:
                {history}
                
                Human: {input}
                AI: """
            )
        )
        
        # Load personality
        self.personality = {
            "name": "AI Influencer",
            "expertise": ["social media", "content creation", "digital marketing", "AI technology"],
            "tone": "professional yet friendly",
            "speaking_style": "engaging and informative"
        }
        
        print("🤖 AI Influencer Chatbot initialized!")
        print("✅ Ready to engage in conversation!")
    
    def generate_complete_post(self, niche: str = "technology", audience: str = "professionals", 
                             tone: str = "engaging", platform: str = "instagram",
                             seo_keywords: List[str] = None) -> Dict[str, Any]:
        """Generate a complete social media post using the Langchain workflow"""
        
        print(f"🎯 Generating {platform} post for {niche} niche...")
        
        try:
            # Step 1: Generate Topic
            print("\n1️⃣ Generating topic...")
            topic_data = self.topic_gen.generate_topic(niche, audience, tone)
            print(f"✅ Topic: {topic_data.get('title', 'Generated')}")
            
            # Step 2: Generate Content
            print("\n2️⃣ Creating content...")
            content_data = self.content_gen.generate_content(topic_data, platform)
            print(f"✅ Content: {content_data.get('character_count', 0)} characters")
            
            # Step 3: Generate Hashtags
            print("\n3️⃣ Optimizing hashtags...")
            hashtag_data = self.hashtag_gen.generate_hashtags(topic_data, content_data, seo_keywords)
            print(f"✅ Hashtags: {hashtag_data.get('total_primary', 0)} primary tags")
            
            # Compile complete post
            complete_post = {
                "post_id": f"ai_influencer_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "generation_timestamp": datetime.now().isoformat(),
                "parameters": {
                    "niche": niche,
                    "audience": audience,
                    "tone": tone,
                    "platform": platform,
                    "seo_keywords": seo_keywords
                },
                "topic": topic_data,
                "content": content_data,
                "hashtags": hashtag_data,
                "ready_to_post": True
            }
            
            # Save the post
            self._save_post(complete_post)
            
            # Add to memory
            self.post_memory.add_post(complete_post)
            
            # Add to conversation memory
            self.conversation_memory.save_context(
                {"input": f"Generate a {platform} post about {niche}"},
                {"output": f"Generated post: {topic_data.get('title', '')}"}
            )
            
            return complete_post
            
        except Exception as e:
            print(f"❌ Error generating complete post: {e}")
            return {
                "error": str(e),
                "ready_to_post": False,
                "generation_timestamp": datetime.now().isoformat()
            }
    
    def _save_post(self, post_data: Dict[str, Any]) -> None:
        """Save post data to organized files"""
        
        # Create organized folders
        posts_dir = "posts"
        os.makedirs(posts_dir, exist_ok=True)
        
        # Get post details for naming
        platform = post_data.get('parameters', {}).get('platform', 'general')
        niche = post_data.get('parameters', {}).get('niche', 'content')
        timestamp = datetime.now().strftime('%y%m%d_%H%M')
        
        # Create filenames
        base_filename = f"{platform}_{niche}_{timestamp}"
        json_path = os.path.join(posts_dir, f"{base_filename}.json")
        txt_path = os.path.join(posts_dir, f"{base_filename}.txt")
        
        try:
            # Save JSON
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(post_data, f, indent=2, ensure_ascii=False)
            print(f"💾 JSON saved: {json_path}")
            
            # Save readable text
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("🤖 AI INFLUENCER SOCIAL MEDIA POST\n")
                f.write("=" * 60 + "\n\n")
                
                # Post metadata
                f.write(f"📝 POST ID: {post_data.get('post_id', 'N/A')}\n")
                f.write(f"📅 Generated: {post_data.get('generation_timestamp', 'N/A')}\n")
                f.write(f"📱 Platform: {platform.title()}\n")
                f.write(f"🎯 Niche: {niche}\n\n")
                
                # Content
                topic = post_data.get('topic', {})
                f.write(f"Title: {topic.get('title', 'N/A')}\n")
                f.write(f"Hook: {topic.get('hook', 'N/A')}\n\n")
                
                content = post_data.get('content', {}).get('content', 'N/A')
                f.write(f"Content:\n{content}\n\n")
                
                # Hashtags
                hashtags = post_data.get('hashtags', {})
                primary_tags = hashtags.get('primary_hashtags', [])
                f.write(f"Hashtags:\n{' '.join(primary_tags)}\n")
            
            print(f"📄 Text file saved: {txt_path}")
            
        except Exception as e:
            print(f"❌ Error saving post: {e}")
    
    def chat(self, user_input: str) -> str:
        """Chat with the user using Langchain conversation chain"""
        try:
            # Get response from conversation chain
            response = self.conversation_chain.predict(input=user_input)
            return response.strip()
        except Exception as e:
            return f"❌ I encountered an error: {str(e)}. Let me try to help you in a simpler way."
    
    def get_post_suggestions(self, platform: str = None, niche: str = None) -> str:
        """Get post suggestions based on previous posts"""
        recent_posts = []
        
        if platform:
            recent_posts = self.post_memory.get_posts_by_platform(platform)
        elif niche:
            recent_posts = self.post_memory.get_posts_by_niche(niche)
        else:
            recent_posts = self.post_memory.get_recent_posts(5)
        
        if not recent_posts:
            return "I don't have any relevant posts to suggest yet. Let's create some!"
        
        # Create prompt for analysis
        posts_context = "\n\n".join([
            f"Post: {post['title']}\nContent: {post['content'][:200]}..."
            for post in recent_posts[:3]
        ])
        
        prompt = f"""
        Based on these recent posts:
        
        {posts_context}
        
        Please suggest:
        1. Content themes that performed well
        2. Hashtag strategies that worked
        3. New post ideas building on successful elements
        4. Ways to improve engagement
        
        Keep suggestions specific and actionable.
        """
        
        try:
            # Using Gemini instead of OpenAI
            from langchain_core.messages import SystemMessage, HumanMessage
            messages = [
                SystemMessage(content="You are an expert social media content analyst."),
                HumanMessage(content=prompt)
            ]
            response = self.config.gemini_llm.invoke(messages)
            
            return response.content.strip()
            
        except Exception as e:
            return f"❌ Error analyzing posts: {str(e)}"
    
    def search_similar_posts(self, query: str) -> str:
        """Search for similar posts and provide insights"""
        matching_posts = self.post_memory.search_posts(query)
        
        if not matching_posts:
            return "I couldn't find any similar posts. Let's create something new!"
        
        # Create prompt for analysis
        posts_context = "\n\n".join([
            f"Post: {post['title']}\nContent: {post['content'][:200]}..."
            for post in matching_posts[:3]
        ])
        
        prompt = f"""
        Analyzing these similar posts for "{query}":
        
        {posts_context}
        
        Please provide:
        1. Common themes and patterns
        2. Successful content strategies
        3. Hashtag combinations that worked well
        4. Suggestions for new, related content
        
        Focus on actionable insights.
        """
        
        try:
            # Using Gemini instead of OpenAI
            from langchain_core.messages import SystemMessage, HumanMessage
            messages = [
                SystemMessage(content="You are an expert social media content analyst."),
                HumanMessage(content=prompt)
            ]
            response = self.config.gemini_llm.invoke(messages)
            
            return response.content.strip()
            
        except Exception as e:
            return f"❌ Error analyzing similar posts: {str(e)}"
    
    def clear_history(self) -> str:
        """Clear the conversation history"""
        self.conversation_memory.clear()
        return "🧹 Conversation history cleared!"

def main():
    """Main function to run the chatbot"""
    
    print("🤖 Welcome to the AI Social Media Influencer Chatbot!")
    print("I can help you with content creation, social media strategy, and more.")
    print("Type 'exit' to end the conversation.")
    print("Type 'help' to see available commands.")
    print("\nAvailable commands:")
    print("- generate post [platform] [niche] [audience]: Generate a complete post")
    print("- suggest posts [platform/niche]: Get post suggestions")
    print("- search posts [query]: Search similar posts")
    print("- chat: Have a conversation about social media strategy")
    print("- clear: Clear conversation history")
    print("- help: Show this help message")
    print("\nLet's create some amazing content! 🚀")
    
    chatbot = AIInfluencerChatbot()
    
    while True:
        user_input = input("\nYou: ").strip().lower()
        
        if user_input == 'exit':
            print("\n👋 Thanks for chatting! Keep creating amazing content!")
            break
            
        elif user_input == 'help':
            print("\nAvailable commands:")
            print("- generate post [platform] [niche] [audience]: Generate a complete post")
            print("- suggest posts [platform/niche]: Get post suggestions")
            print("- search posts [query]: Search similar posts")
            print("- chat: Have a conversation about social media strategy")
            print("- clear: Clear conversation history")
            print("- help: Show this help message")
            print("- exit: End the conversation")
            
        elif user_input.startswith('generate post'):
            parts = user_input.split()
            platform = parts[2] if len(parts) > 2 else "instagram"
            niche = parts[3] if len(parts) > 3 else "technology"
            audience = parts[4] if len(parts) > 4 else "professionals"
            
            complete_post = chatbot.generate_complete_post(
                platform=platform,
                niche=niche,
                audience=audience
            )
            
            if complete_post.get("ready_to_post"):
                print("\n✅ Post generated successfully!")
                print(f"\n📝 Title: {complete_post['topic']['title']}")
                print(f"\n💡 Content:")
                print("-" * 40)
                print(complete_post['content']['content'])
                print("-" * 40)
                print(f"\n🏷️ Hashtags:")
                print(" ".join(complete_post['hashtags']['primary_hashtags']))
                print(f"\n💾 Post saved to: posts/{platform}_{niche}_{datetime.now().strftime('%y%m%d_%H%M')}.txt")
            else:
                print(f"\n❌ Error generating post: {complete_post.get('error', 'Unknown error')}")
            
        elif user_input.startswith('suggest posts'):
            parts = user_input.split()
            filter_type = parts[2] if len(parts) > 2 else None
            suggestions = chatbot.get_post_suggestions(
                platform=filter_type if filter_type in ["instagram", "linkedin", "twitter"] else None,
                niche=filter_type if filter_type not in ["instagram", "linkedin", "twitter"] else None
            )
            print(f"\n🤖 AI Influencer: {suggestions}")
            
        elif user_input.startswith('search posts'):
            query = ' '.join(user_input.split()[2:])
            if query:
                results = chatbot.search_similar_posts(query)
                print(f"\n🤖 AI Influencer: {results}")
            else:
                print("\n❌ Please provide a search query")
            
        elif user_input == 'clear':
            response = chatbot.clear_history()
            print(f"\n🤖 AI Influencer: {response}")
            
        else:
            response = chatbot.chat(user_input)
            print(f"\n🤖 AI Influencer: {response}")

if __name__ == "__main__":
    main()