# 使用task-master规划任务

**页面ID:** 2757995750  
**URL:** https://confluence.shopee.io/pages/viewpage.action?pageId=2757995750

## 安装MCP

[claude-task-master](https://github.com/eyaltoledano/claude-task-master)

## 使用步骤

* 使用chatgpt/gemini/...生成项目PRD文档
* 使用taskmanager初始化

  Can you please initialize taskmaster-ai into my project?
* 使用prd文档拆分task

  Please use the task-master parse-prd command to generate tasks from my PRD. The PRD is located at scripts/prd.txt.
  I've just initialized a new project with Claude Task Master. I have a PRD at scripts/prd.txt.
  Can you help me parse it and set up the initial tasks?
* 子任务拆分

  Task 5 seems complex. Can you break it down into subtasks?
* 任务/子任务执行

  What tasks are available to work on next?
  Let's implement task 3. What does it involve?
  I'd like to implement task 4. Can you help me understand what needs to be done and how to approach it?
* 任务变更

  We've decided to use MongoDB instead of PostgreSQL. Can you update all future tasks to reflect this change?