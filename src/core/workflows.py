"""
Workflow Chains
Pre-defined multi-step workflows for common tasks
"""

from typing import Dict, List, Tuple, Any


class WorkflowExecutor:
    """Executes pre-defined workflow chains."""
    
    # Workflow definitions
    WORKFLOWS = {
        "coding_session": {
            "description": "Prepare for coding",
            "steps": [
                ("open_app", {"app": "VS Code"}),
                ("open_app", {"app": "Terminal"}),
                ("open_app", {"app": "Chrome"}),
                ("switch_mode", {"mode": "coding"}),
                ("set_volume", {"level": 40}),
            ]
        },
        "research_session": {
            "description": "Prepare for research",
            "steps": [
                ("open_app", {"app": "Chrome"}),
                ("open_app", {"app": "Notes"}),
                ("switch_mode", {"mode": "research"}),
                ("set_volume", {"level": 60}),
            ]
        },
        "end_session": {
            "description": "End work session",
            "steps": [
                ("close_app", {"app": "VS Code"}),
                ("close_app", {"app": "Terminal"}),
                ("open_app", {"app": "Mail"}),
                ("switch_mode", {"mode": "general"}),
                ("set_volume", {"level": 70}),
            ]
        },
        "study_session": {
            "description": "Prepare for studying",
            "steps": [
                ("open_app", {"app": "Notes"}),
                ("open_app", {"app": "Chrome"}),
                ("set_volume", {"level": 50}),
                ("switch_mode", {"mode": "research"}),
            ]
        }
    }
    
    def __init__(self, agent):
        """Initialize with reference to main agent."""
        self.agent = agent
    
    def list_workflows(self) -> List[str]:
        """Get list of available workflows."""
        return list(self.WORKFLOWS.keys())
    
    def get_workflow_description(self, workflow_name: str) -> str:
        """Get description of a workflow."""
        if workflow_name in self.WORKFLOWS:
            return self.WORKFLOWS[workflow_name]["description"]
        return "Unknown workflow"
    
    def execute(self, workflow_name: str) -> Tuple[bool, str]:
        """
        Execute a workflow.
        
        Returns:
            (success: bool, message: str)
        """
        if workflow_name not in self.WORKFLOWS:
            available = ", ".join(self.list_workflows())
            return (False, f"Unknown workflow, sir. Available: {available}")
        
        workflow = self.WORKFLOWS[workflow_name]
        steps = workflow["steps"]
        results = []
        
        for action, params in steps:
            try:
                if action == "open_app":
                    success, msg = self.agent.mac_control.open_app(params["app"])
                    if success:
                        results.append(f"opened {params['app']}")
                
                elif action == "close_app":
                    success, msg = self.agent.mac_control.close_app(params["app"])
                    if success:
                        results.append(f"closed {params['app']}")
                
                elif action == "switch_mode":
                    self.agent.switch_model(params["mode"])
                    results.append(f"switched to {params['mode']} mode")
                
                elif action == "set_volume":
                    success, msg = self.agent.mac_control.set_volume(params["level"])
                    if success:
                        results.append(f"set volume to {params['level']}%")
                
            except Exception as e:
                print(f"Workflow step failed: {e}")
                continue
        
        if results:
            summary = ", ".join(results)
            return (True, f"Workflow complete, sir. I've {summary}.")
        else:
            return (False, "Workflow execution failed, sir.")
