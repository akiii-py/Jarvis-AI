
from src.integrations.web_scraper import WebScraper
from src.core.llm import LLMClient
from src.config.config import Config
import datetime
import os

class ResearchAgent:
    """
    Conducts deep research on a topic and generates a report.
    Uses WebScraper to get data and LLM to synthesize it.
    """
    
    def __init__(self, llm_client: LLMClient):
        self.scraper = WebScraper()
        self.llm = llm_client
        self.reports_dir = Config.DATA_DIR / "research_reports"
        self.reports_dir.mkdir(exist_ok=True)
        
    def conduct_research(self, topic: str) -> str:
        """Execute full research workflow."""
        start_time = datetime.datetime.now()
        
        # 1. Gather Data
        raw_data = self.scraper.research_topic(topic)
        
        if not raw_data:
            return "I'm afraid I couldn't find any sources on that topic, sir."
            
        # 2. Synthesize with LLM
        print("🧠 Synthesizing information...")
        
        # Prepare context for LLM
        context = f"Research Topic: {topic}\n\nSources Data:\n"
        for url, text in raw_data.items():
            context += f"--- Source: {url} ---\n{text[:2000]}\n\n"
            
        prompt = f"""
        You are JARVIS, a sophisticated research assistant.
        Analyze the provided text from multiple sources and write a comprehensive research summary on: "{topic}".
        
        Format the output in clear Markdown with:
        - Main Breakdown of the topic
        - Key findings/Pros & Cons
        - Source citations (URLs)
        
        Keep it concise but technical.
        """
        
        # We use the research model (deepseek-r1) if available, otherwise current model
        # For simplicity in this implementation, we use the current attached LLM text generation
        # direct generation call
        
        try:
             # Using the existing LLM client generator
             response_gen = self.llm.chat([
                 {"role": "system", "content": prompt},
                 {"role": "user", "content": context}
             ], stream=False, use_jarvis_personality=False)
             
             report_content = "".join(list(response_gen))
             
        except Exception as e:
            return f"Error during synthesis: {e}"
            
        # 3. Save Report
        filename = f"Research_{topic.replace(' ', '_')}_{start_time.strftime('%Y%m%d')}.md"
        filepath = self.reports_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(f"# Research Report: {topic}\n")
            f.write(f"Date: {start_time.strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write(report_content)
            
        return f"Research complete, sir. I've analyzed {len(raw_data)} sources. \n\n**Summary:**\n{report_content[:500]}...\n\n(Full report saved to {filepath})"
