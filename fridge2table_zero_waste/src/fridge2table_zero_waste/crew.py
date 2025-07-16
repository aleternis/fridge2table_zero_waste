import os
print("GOOGLE_API_KEY present:", os.getenv("GOOGLE_API_KEY", "Not found")[:5] + "...")
print("GEMINI_API_KEY present:", os.getenv("GEMINI_API_KEY", "Not found")[:5] + "...")
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from .tools.custom_tool import ImageToTextTool
from dotenv import load_dotenv
load_dotenv()  # This will read .env and set environment variables

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators


@CrewBase
class Fridge2TableZeroWaste:
    """Fridge2TableZeroWaste crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    image_tool  = ImageToTextTool()


    @agent
    def vision_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['vision_agent'],
            verbose=True,
            tools=[ImageToTextTool.identify_fridge_items],
            max_iter=1
        )

    @agent
    def inventory_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['inventory_agent'],
            verbose=True,
        )

    @agent
    def meal_planner_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['meal_planner_agent'],
            verbose=True,
        )

    @agent
    def recipe_finder_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['recipe_finder_agent'],
            verbose=True,
        )

    @task
    def analyze_fridge_photo(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_fridge_photo'],
        )

    @task
    def update_inventory(self) -> Task:
        return Task(
            config=self.tasks_config['update_inventory'],
        )

    @task
    def suggest_meal_plan(self) -> Task:
        return Task(
            config=self.tasks_config['suggest_meal_plan'],
        )

    @task
    def find_recipes(self) -> Task:
        return Task(
            config=self.tasks_config['find_recipes'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Fridge2TableZeroWaste crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )