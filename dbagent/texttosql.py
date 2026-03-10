from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent

# # OpenAI model
# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# # connect database
# db = SQLDatabase.from_uri(
#     "postgresql://user:password@host:5432/mydb"
# )

# # create SQL agent
# agent = create_sql_agent(llm, db=db, verbose=True)

# # ask question
# agent.invoke({
#     "input": "How many users are in the database?"
# })