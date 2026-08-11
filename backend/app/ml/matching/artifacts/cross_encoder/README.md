---
tags:
- sentence-transformers
- cross-encoder
- reranker
- generated_from_trainer
- dataset_size:17658
- loss:BinaryCrossEntropyLoss
base_model: cross-encoder/stsb-roberta-base
pipeline_tag: text-ranking
library_name: sentence-transformers
---

# CrossEncoder based on cross-encoder/stsb-roberta-base

This is a [Cross Encoder](https://www.sbert.net/docs/cross_encoder/usage/usage.html) model finetuned from [cross-encoder/stsb-roberta-base](https://huggingface.co/cross-encoder/stsb-roberta-base) using the [sentence-transformers](https://www.SBERT.net) library. It computes scores for pairs of texts, which can be used for text reranking and semantic search.

## Model Details

### Model Description
- **Model Type:** Cross Encoder
- **Base model:** [cross-encoder/stsb-roberta-base](https://huggingface.co/cross-encoder/stsb-roberta-base) <!-- at revision d576534b67143e2c70ee9966d7fdbf5835728d13 -->
- **Maximum Sequence Length:** 256 tokens
- **Number of Output Labels:** 1 label
- **Supported Modality:** Text
<!-- - **Training Dataset:** Unknown -->
<!-- - **Language:** Unknown -->
<!-- - **License:** Unknown -->

### Model Sources

- **Documentation:** [Sentence Transformers Documentation](https://sbert.net)
- **Documentation:** [Cross Encoder Documentation](https://www.sbert.net/docs/cross_encoder/usage/usage.html)
- **Repository:** [Sentence Transformers on GitHub](https://github.com/huggingface/sentence-transformers)
- **Hugging Face:** [Cross Encoders on Hugging Face](https://huggingface.co/models?library=sentence-transformers&other=cross-encoder)

### Full Model Architecture

```
CrossEncoder(
  (0): Transformer({'transformer_task': 'sequence-classification', 'modality_config': {'text': {'method': 'forward', 'method_output_name': 'logits'}}, 'module_output_name': 'scores', 'architecture': 'RobertaForSequenceClassification'})
)
```

## Usage

### Direct Usage (Sentence Transformers)

First install the Sentence Transformers library:

```bash
pip install -U sentence-transformers
```

Then you can load this model and run inference.
```python
from sentence_transformers import CrossEncoder

# Download from the 🤗 Hub
model = CrossEncoder("cross_encoder_model_id")
# Get scores for pairs of inputs
pairs = [
    ['Domain: Web Development, Frontend Development, Full Stack. Technical skills: css, html, java, javascript, machine learning, mongodb, natural language processing, node.js, python, react, sql. Experience years: 0.0', "Job title: Senior Site Reliability Engineer. Company: Ideagen Plc.. Description: Role Purpose\nIdeagen\xa0is the invisible force behind many things we rely on every day - from keeping airplanes soaring in the sky, to ensuring the food on our tables is safe, to helping doctors and nurses care for the sick. So, when you think of\xa0Ideagen, think of it as the silent teammate\xa0that's\xa0always working behind the scenes to help those people who make our lives safer and better.\nEvery day millions of people are kept safe using Ideagen software. We have offices all over the world including America, Australia, Malaysia and India with people doing lots of different and exciting jobs.\nIdeagen believe that by recruiting diverse and talented individuals, we create an inclusive community for all. We are committed to empowering all colleagues to maximise their potential and express their unique characteristics, experience, and knowledge to achieve their ambitions.\nResponsibilities\n• Manage, monitor, and maintain our infrastructure platforms across a multi-cloud environment.\n• Manage design, development, and operational changes to cloud based infrastructure services.\n• Provide operational support and be able to co-ordinate with other teams during incidents that may impact service.\n• Work to improve the reliability, quality, performance, and scalability of our infrastructure.\n• Continually measure and optimise system performance.\n• Enable the engineering organization to innovate and deliver with greater speed and safety\nSkills and Experience\nWe don’t expect you to be an expert in everything but with our technology stack experience of some of the following is essential:\nExperience in production 24/7 high-availability SaaS environments based on AWS.\nExperience of working with orchestration and containerisation e.g. Docker, Kubernetes, EKS/AKS etc\nDeep knowledge of AWS tools and products, that follow the AWS Well-Architected Framework.\nExperience of working alongside development functions delivering software within an agile development environment.\nStrong scripting skills in various languages such as Python, BASH, and/or PowerShell.\nWorking alongside development functions delivering software within an agile development environment.\nMust be a team player, with exceptional communication skills, working well with others in the group and the rest of the engineering organization.\nFamiliarity with Cloud security and governance models.\nProven ability to grasp new technical concepts quickly.\nDesirable:\nStrong understanding of Software Development Lifecycles\nExperience with designing & architecting distributed systems on AWS.\nExperience of CI/CD such as Jenkins, GitLab, Azure DevOps etc.\nExperience with Infrastructure as Code (IaC) tools such as Terraform, CloudFormation\nKnowledge on Automation tools.\nGood to have knowledge on Grafana, Prometheus.\nknowledge of Linux troubleshooting, including networking, file systems, security, and the kernel.\nExperience with compliance standards based infrastructure such as ISO27001, Cyber Essentials & FedRAMP, and general regulatory compliance management.\nExposure to ITIL concepts and adoption.\nBehavioral\nAmbitious - Drive, Planning & Execution\nAdventurous - Flexibility & Resilience and Savvy Thinking\nCommunity - Collaboration & Communication. Required skills: aws, azure, ci/cd, cloudformation, docker, express.js, git, kubernetes, linux, python, shell/bash, terraform. Domain: Cloud / DevOps, Web Development, Backend Development. Experience required: 0.0"],
    ['Domain: Web Development, Frontend Development, Full Stack. Technical skills: bootstrap, css, figma, firebase, git, html, java, javascript, machine learning, material-ui, mongodb, mysql, node.js, os, postman, python, react, tailwind css. Experience years: 0.0', 'Job title: Senior Software Developer (Telecommunications). Company: DCConnect Global. Description: SENIOR SOFTWARE ENGINEER (Telco)\nJOB DESCRIPTION\nDevelop and maintain our flagship BSS/OSS system for SDN (software defined networking) and SD-WAN (software defined wide area network).\nWork on cutting-edge SDN products and web portals.\nParticipate in the entire software life-cycle including development, testing and debugging following an agile DevOps model.\nResearch and evaluate the latest software technologies in order to meet user requirements.\nWrite technical documentation for our partners and team members.\nCORE REQUIREMENTS\nHigher Diploma or Degree holder in Computer Science or related disciplines, fresh graduates with a passion for software development or computer networks are welcome to apply\nHighly experienced with Web application development in frontend and backend\n(TypeScript, Node.js, React, GIT, JSON, CSS, RESTful web services, at least one relational database like MySQL/MariaDB or Postgres)\nStrong ability to work under pressure and meet tight deadlines\nAt least 2 years of experience in related fields. Candidates with more experience will be considered for Senior Software Engineer\nEnthusiastic about new technology!\nPreferably to START immediately or within a short notice\nDESIRABLE SKILLS\nExperience in Java, relational databases, object-oriented programming principles\nExperience with Specification by Example (SbE), A-TDD, and associated tooling, e.g., cucumber\nBasic to advanced knowledge of Linux commands and server administration\nAn understanding in computer networking (OSI Model, BGP, routing, TCP/IP)\nExperience with Docker and other DevOps technologies\nExperience in Android/IOS app development. Required skills: a-tdd, android, bgp, css, docker, git, ios, java, json, linux, mysql, node.js, postgresql, react, typescript. Domain: Web Development, Full Stack, Backend Development. Experience required: 2.0'],
    ['Domain: Web Development, Machine Learning / AI, Full Stack. Technical skills: c++, css, deep learning, docker, express.js, firebase, flutter, git, google cloud, html, java, javascript, machine learning, matlab, mongodb, natural language processing, node.js, python, quantum computing, react, ruby, scikit-learn, spring boot, sql, tensorflow, unity, wordpress. Experience years: 0.8', 'Job title: Senior Java Developer (Microservices). Company: JP Caliber. Description: Requirements\n5+ years of software development experience in Java 8.\nExperience in developing microservices using Spring Boot. Experience in security, transaction, Idempotency, log tracing, distributed caching, monitoring, and containerization requirements of microservices. Experience in developing High Cohesion & Loosely Coupled Micro Services.\nStrong experience in Spring Framework such as Spring Cloud, Spring Boot, Spring Data, Spring Security, Spring Batch, Spring AOP and others.\xa0Extensive experience in developing Microservices using Netflix OSS (Zuul, Eureka, Ribbon, Hystrix), Feign Client, Sleuth and Zipkin.\nWorking experience in Industry Standard protocols related to API Security including OAuth.\nShould have excellent acumen in Data Structures, algorithms, problem-solving and Logical/Analytical skills. Thorough understanding of OOPS concepts, Design principles and implementation of different types of Design patterns.\nSound understanding of concepts like Exceptional handling, Serialization/Deserialization and Immutability concepts, etc. Good fundamental knowledge of Enums, Collections, Annotations, Generics, Autoboxing, etc.\nExperience with Multithreading, Concurrent Packages, and Concurrent APIs.\nBasic understanding of Java Memory Management (JMM) including garbage collection concepts.\nExperience in RDBMS or NO SQL databases and writing SQL queries (Joins, group by, aggregate functions, etc.). Working knowledge of SQL/No-SQL and database technologies (Oracle, MySQL, Mongo DB, Cosmos DB). Expertise in JPA, Hibernate, and SQL.\nHands-on experience with Message brokers like Kafka or others.\nHands-on experience in creating RESTful web services and consuming web services.\nHands-on experience with any of the logging frameworks (SLF4J/LogBack/Log4j)\nExperience in writing Junit test cases using Mockito / Power mock frameworks.\nShould have practical experience with Maven/Gradle and knowledge of version control systems like Git/SVN etc.\nNice to have:\xa0Experience working on these front-end technologies such as HTML5, CSS3, and JavaScript along with React & Node JS frameworks.\nKnowledge in developing and deploying solutions on any of these cloud platforms (AWS, Azure, GCP) and containerized ecosystems (Docker, Kubernetes)\nSummary of role requirements:\nLooking for candidates available to work:\nMonday: Morning\nTuesday: Morning\nWednesday: Morning\nThursday: Morning\nFriday: Morning\nMore than 4 years of relevant work experience required for this role\nWorking rights required for this role\nExpected salary: RM7,000 - RM14,000 per month. Required skills: aws, azure, css, docker, git, google cloud, html, java, javascript, kafka, kubernetes, mongodb, mysql, node.js, react, spring boot, sql. Domain: Web Development, Cloud / DevOps, Backend Development. Experience required: 4.0'],
    ['Domain: Web Development, Full Stack, Backend Development. Technical skills: autocad, django, express.js, figma, firebase, git, java, javascript, mongodb, mysql, nestjs, next.js, node.js, php, postgresql, python, react. Experience years: 0.2', 'Job title: Senior Software Developer (Telecommunications). Company: DCConnect Global. Description: SENIOR SOFTWARE ENGINEER (Telco)\nJOB DESCRIPTION\nDevelop and maintain our flagship BSS/OSS system for SDN (software defined networking) and SD-WAN (software defined wide area network).\nWork on cutting-edge SDN products and web portals.\nParticipate in the entire software life-cycle including development, testing and debugging following an agile DevOps model.\nResearch and evaluate the latest software technologies in order to meet user requirements.\nWrite technical documentation for our partners and team members.\nCORE REQUIREMENTS\nHigher Diploma or Degree holder in Computer Science or related disciplines, fresh graduates with a passion for software development or computer networks are welcome to apply\nHighly experienced with Web application development in frontend and backend\n(TypeScript, Node.js, React, GIT, JSON, CSS, RESTful web services, at least one relational database like MySQL/MariaDB or Postgres)\nStrong ability to work under pressure and meet tight deadlines\nAt least 2 years of experience in related fields. Candidates with more experience will be considered for Senior Software Engineer\nEnthusiastic about new technology!\nPreferably to START immediately or within a short notice\nDESIRABLE SKILLS\nExperience in Java, relational databases, object-oriented programming principles\nExperience with Specification by Example (SbE), A-TDD, and associated tooling, e.g., cucumber\nBasic to advanced knowledge of Linux commands and server administration\nAn understanding in computer networking (OSI Model, BGP, routing, TCP/IP)\nExperience with Docker and other DevOps technologies\nExperience in Android/IOS app development. Required skills: a-tdd, android, bgp, css, docker, git, ios, java, json, linux, mysql, node.js, postgresql, react, typescript. Domain: Web Development, Full Stack, Backend Development. Experience required: 2.0'],
    ['Domain: General Engineering. Technical skills: harshdashpute03, laems, python. Experience years: 0.2', 'Job title: Internship for IT Infrastructure (Up to RM2000 for top and qualified students). Company: iFAST Capital Sdn Bhd. Description: Up to RM2,000 for Top Students\nResponsibilities:\nTo provide 1st level user support.\nTo manage office endpoint deployment.\nTo manage office hardware and software inventory.\nTo manage update and upgrade of all office servers and endpoints.\nTo deploy and maintain office VOIP system and phones, audio systems and other devices.\nTo perform regular health and audit check on all office devices, endpoints, and servers.\nTo perform Active Directory, Email, and various Access Rights administrations.\nTo undertake any ad-hoc matters and projects assigned from time to time.\nRequirements:\nCandidate must possess at least a Degree of Computer Science / Information Technology in Network / Database / Security or equivalent.\nStrong critical thinking, analytical skills, and problem-solving skills.\nAdaptive to different situations; attentive and proactive to issues; team-oriented person.\nAdditional technical advantages:\nMCSA, MCSE, CCNA, ITIL\nor any other professional certificate.\nKnowledge in\nMS AD, DNS, DHCP, WSUS, GPO, UNIX, Hyper-V, VMware vSphere\nUNIX / Windows scripting experience\nAvailable for duration of 3 to 6 months.\nApplicants who are interested in this role are invited to apply with their comprehensive resume with full details via "Apply Now" button with:\n(1) Qualifications\n(2) Skills\n(3) Working Experience\n(4) Expected Salary\n** Kindly attach a copy of your academic transcripts and certifications together with your resume **\nAll applications will be treated in strict confidence. We regret that only shortlisted applicants will be notified.\nNote: Job responsibilities / requirements are representative and are not intended to be a detailed list. Other tasks/abilities may be required of the incumbent, relative to the specific assignment.. Required skills: ccna, dhcp, dns, gpo, hyper-v, itil, mcsa, mcse, unix, wsus. Domain: General Engineering. Experience required: 0.0'],
]
scores = model.predict(pairs)
print(scores)
# [0.008  0.9696 0.9975 0.9931 0.0071]

# Or rank different texts based on similarity to a single text
ranks = model.rank(
    'Domain: Web Development, Frontend Development, Full Stack. Technical skills: css, html, java, javascript, machine learning, mongodb, natural language processing, node.js, python, react, sql. Experience years: 0.0',
    [
        "Job title: Senior Site Reliability Engineer. Company: Ideagen Plc.. Description: Role Purpose\nIdeagen\xa0is the invisible force behind many things we rely on every day - from keeping airplanes soaring in the sky, to ensuring the food on our tables is safe, to helping doctors and nurses care for the sick. So, when you think of\xa0Ideagen, think of it as the silent teammate\xa0that's\xa0always working behind the scenes to help those people who make our lives safer and better.\nEvery day millions of people are kept safe using Ideagen software. We have offices all over the world including America, Australia, Malaysia and India with people doing lots of different and exciting jobs.\nIdeagen believe that by recruiting diverse and talented individuals, we create an inclusive community for all. We are committed to empowering all colleagues to maximise their potential and express their unique characteristics, experience, and knowledge to achieve their ambitions.\nResponsibilities\n• Manage, monitor, and maintain our infrastructure platforms across a multi-cloud environment.\n• Manage design, development, and operational changes to cloud based infrastructure services.\n• Provide operational support and be able to co-ordinate with other teams during incidents that may impact service.\n• Work to improve the reliability, quality, performance, and scalability of our infrastructure.\n• Continually measure and optimise system performance.\n• Enable the engineering organization to innovate and deliver with greater speed and safety\nSkills and Experience\nWe don’t expect you to be an expert in everything but with our technology stack experience of some of the following is essential:\nExperience in production 24/7 high-availability SaaS environments based on AWS.\nExperience of working with orchestration and containerisation e.g. Docker, Kubernetes, EKS/AKS etc\nDeep knowledge of AWS tools and products, that follow the AWS Well-Architected Framework.\nExperience of working alongside development functions delivering software within an agile development environment.\nStrong scripting skills in various languages such as Python, BASH, and/or PowerShell.\nWorking alongside development functions delivering software within an agile development environment.\nMust be a team player, with exceptional communication skills, working well with others in the group and the rest of the engineering organization.\nFamiliarity with Cloud security and governance models.\nProven ability to grasp new technical concepts quickly.\nDesirable:\nStrong understanding of Software Development Lifecycles\nExperience with designing & architecting distributed systems on AWS.\nExperience of CI/CD such as Jenkins, GitLab, Azure DevOps etc.\nExperience with Infrastructure as Code (IaC) tools such as Terraform, CloudFormation\nKnowledge on Automation tools.\nGood to have knowledge on Grafana, Prometheus.\nknowledge of Linux troubleshooting, including networking, file systems, security, and the kernel.\nExperience with compliance standards based infrastructure such as ISO27001, Cyber Essentials & FedRAMP, and general regulatory compliance management.\nExposure to ITIL concepts and adoption.\nBehavioral\nAmbitious - Drive, Planning & Execution\nAdventurous - Flexibility & Resilience and Savvy Thinking\nCommunity - Collaboration & Communication. Required skills: aws, azure, ci/cd, cloudformation, docker, express.js, git, kubernetes, linux, python, shell/bash, terraform. Domain: Cloud / DevOps, Web Development, Backend Development. Experience required: 0.0",
        'Job title: Senior Software Developer (Telecommunications). Company: DCConnect Global. Description: SENIOR SOFTWARE ENGINEER (Telco)\nJOB DESCRIPTION\nDevelop and maintain our flagship BSS/OSS system for SDN (software defined networking) and SD-WAN (software defined wide area network).\nWork on cutting-edge SDN products and web portals.\nParticipate in the entire software life-cycle including development, testing and debugging following an agile DevOps model.\nResearch and evaluate the latest software technologies in order to meet user requirements.\nWrite technical documentation for our partners and team members.\nCORE REQUIREMENTS\nHigher Diploma or Degree holder in Computer Science or related disciplines, fresh graduates with a passion for software development or computer networks are welcome to apply\nHighly experienced with Web application development in frontend and backend\n(TypeScript, Node.js, React, GIT, JSON, CSS, RESTful web services, at least one relational database like MySQL/MariaDB or Postgres)\nStrong ability to work under pressure and meet tight deadlines\nAt least 2 years of experience in related fields. Candidates with more experience will be considered for Senior Software Engineer\nEnthusiastic about new technology!\nPreferably to START immediately or within a short notice\nDESIRABLE SKILLS\nExperience in Java, relational databases, object-oriented programming principles\nExperience with Specification by Example (SbE), A-TDD, and associated tooling, e.g., cucumber\nBasic to advanced knowledge of Linux commands and server administration\nAn understanding in computer networking (OSI Model, BGP, routing, TCP/IP)\nExperience with Docker and other DevOps technologies\nExperience in Android/IOS app development. Required skills: a-tdd, android, bgp, css, docker, git, ios, java, json, linux, mysql, node.js, postgresql, react, typescript. Domain: Web Development, Full Stack, Backend Development. Experience required: 2.0',
        'Job title: Senior Java Developer (Microservices). Company: JP Caliber. Description: Requirements\n5+ years of software development experience in Java 8.\nExperience in developing microservices using Spring Boot. Experience in security, transaction, Idempotency, log tracing, distributed caching, monitoring, and containerization requirements of microservices. Experience in developing High Cohesion & Loosely Coupled Micro Services.\nStrong experience in Spring Framework such as Spring Cloud, Spring Boot, Spring Data, Spring Security, Spring Batch, Spring AOP and others.\xa0Extensive experience in developing Microservices using Netflix OSS (Zuul, Eureka, Ribbon, Hystrix), Feign Client, Sleuth and Zipkin.\nWorking experience in Industry Standard protocols related to API Security including OAuth.\nShould have excellent acumen in Data Structures, algorithms, problem-solving and Logical/Analytical skills. Thorough understanding of OOPS concepts, Design principles and implementation of different types of Design patterns.\nSound understanding of concepts like Exceptional handling, Serialization/Deserialization and Immutability concepts, etc. Good fundamental knowledge of Enums, Collections, Annotations, Generics, Autoboxing, etc.\nExperience with Multithreading, Concurrent Packages, and Concurrent APIs.\nBasic understanding of Java Memory Management (JMM) including garbage collection concepts.\nExperience in RDBMS or NO SQL databases and writing SQL queries (Joins, group by, aggregate functions, etc.). Working knowledge of SQL/No-SQL and database technologies (Oracle, MySQL, Mongo DB, Cosmos DB). Expertise in JPA, Hibernate, and SQL.\nHands-on experience with Message brokers like Kafka or others.\nHands-on experience in creating RESTful web services and consuming web services.\nHands-on experience with any of the logging frameworks (SLF4J/LogBack/Log4j)\nExperience in writing Junit test cases using Mockito / Power mock frameworks.\nShould have practical experience with Maven/Gradle and knowledge of version control systems like Git/SVN etc.\nNice to have:\xa0Experience working on these front-end technologies such as HTML5, CSS3, and JavaScript along with React & Node JS frameworks.\nKnowledge in developing and deploying solutions on any of these cloud platforms (AWS, Azure, GCP) and containerized ecosystems (Docker, Kubernetes)\nSummary of role requirements:\nLooking for candidates available to work:\nMonday: Morning\nTuesday: Morning\nWednesday: Morning\nThursday: Morning\nFriday: Morning\nMore than 4 years of relevant work experience required for this role\nWorking rights required for this role\nExpected salary: RM7,000 - RM14,000 per month. Required skills: aws, azure, css, docker, git, google cloud, html, java, javascript, kafka, kubernetes, mongodb, mysql, node.js, react, spring boot, sql. Domain: Web Development, Cloud / DevOps, Backend Development. Experience required: 4.0',
        'Job title: Senior Software Developer (Telecommunications). Company: DCConnect Global. Description: SENIOR SOFTWARE ENGINEER (Telco)\nJOB DESCRIPTION\nDevelop and maintain our flagship BSS/OSS system for SDN (software defined networking) and SD-WAN (software defined wide area network).\nWork on cutting-edge SDN products and web portals.\nParticipate in the entire software life-cycle including development, testing and debugging following an agile DevOps model.\nResearch and evaluate the latest software technologies in order to meet user requirements.\nWrite technical documentation for our partners and team members.\nCORE REQUIREMENTS\nHigher Diploma or Degree holder in Computer Science or related disciplines, fresh graduates with a passion for software development or computer networks are welcome to apply\nHighly experienced with Web application development in frontend and backend\n(TypeScript, Node.js, React, GIT, JSON, CSS, RESTful web services, at least one relational database like MySQL/MariaDB or Postgres)\nStrong ability to work under pressure and meet tight deadlines\nAt least 2 years of experience in related fields. Candidates with more experience will be considered for Senior Software Engineer\nEnthusiastic about new technology!\nPreferably to START immediately or within a short notice\nDESIRABLE SKILLS\nExperience in Java, relational databases, object-oriented programming principles\nExperience with Specification by Example (SbE), A-TDD, and associated tooling, e.g., cucumber\nBasic to advanced knowledge of Linux commands and server administration\nAn understanding in computer networking (OSI Model, BGP, routing, TCP/IP)\nExperience with Docker and other DevOps technologies\nExperience in Android/IOS app development. Required skills: a-tdd, android, bgp, css, docker, git, ios, java, json, linux, mysql, node.js, postgresql, react, typescript. Domain: Web Development, Full Stack, Backend Development. Experience required: 2.0',
        'Job title: Internship for IT Infrastructure (Up to RM2000 for top and qualified students). Company: iFAST Capital Sdn Bhd. Description: Up to RM2,000 for Top Students\nResponsibilities:\nTo provide 1st level user support.\nTo manage office endpoint deployment.\nTo manage office hardware and software inventory.\nTo manage update and upgrade of all office servers and endpoints.\nTo deploy and maintain office VOIP system and phones, audio systems and other devices.\nTo perform regular health and audit check on all office devices, endpoints, and servers.\nTo perform Active Directory, Email, and various Access Rights administrations.\nTo undertake any ad-hoc matters and projects assigned from time to time.\nRequirements:\nCandidate must possess at least a Degree of Computer Science / Information Technology in Network / Database / Security or equivalent.\nStrong critical thinking, analytical skills, and problem-solving skills.\nAdaptive to different situations; attentive and proactive to issues; team-oriented person.\nAdditional technical advantages:\nMCSA, MCSE, CCNA, ITIL\nor any other professional certificate.\nKnowledge in\nMS AD, DNS, DHCP, WSUS, GPO, UNIX, Hyper-V, VMware vSphere\nUNIX / Windows scripting experience\nAvailable for duration of 3 to 6 months.\nApplicants who are interested in this role are invited to apply with their comprehensive resume with full details via "Apply Now" button with:\n(1) Qualifications\n(2) Skills\n(3) Working Experience\n(4) Expected Salary\n** Kindly attach a copy of your academic transcripts and certifications together with your resume **\nAll applications will be treated in strict confidence. We regret that only shortlisted applicants will be notified.\nNote: Job responsibilities / requirements are representative and are not intended to be a detailed list. Other tasks/abilities may be required of the incumbent, relative to the specific assignment.. Required skills: ccna, dhcp, dns, gpo, hyper-v, itil, mcsa, mcse, unix, wsus. Domain: General Engineering. Experience required: 0.0',
    ]
)
# [{'corpus_id': ..., 'score': ...}, {'corpus_id': ..., 'score': ...}, ...]
```

<!--
### Direct Usage (Transformers)

<details><summary>Click to see the direct usage in Transformers</summary>

</details>
-->

<!--
### Downstream Usage (Sentence Transformers)

You can finetune this model on your own dataset.

<details><summary>Click to expand</summary>

</details>
-->

<!--
### Out-of-Scope Use

*List how the model may foreseeably be misused and address what users ought not to do with the model.*
-->

<!--
## Bias, Risks and Limitations

*What are the known or foreseeable issues stemming from this model? You could also flag here known failure cases or weaknesses of the model.*
-->

<!--
### Recommendations

*What are recommendations with respect to the foreseeable issues? For example, filtering explicit content.*
-->

## Training Details

### Training Dataset

#### Unnamed Dataset

* Size: 17,658 training samples
* Columns: <code>sentence_0</code>, <code>sentence_1</code>, and <code>label</code>
* Approximate statistics based on the first 100 samples:
  |          | sentence_0                                                                          | sentence_1                                                                            | label                                                          |
  |:---------|:------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------|:---------------------------------------------------------------|
  | type     | string                                                                              | string                                                                                | float                                                          |
  | modality | text                                                                                | text                                                                                  |                                                                |
  | details  | <ul><li>min: 19 tokens</li><li>mean: 54.08 tokens</li><li>max: 151 tokens</li></ul> | <ul><li>min: 147 tokens</li><li>mean: 250.99 tokens</li><li>max: 256 tokens</li></ul> | <ul><li>min: 0.0</li><li>mean: 0.41</li><li>max: 1.0</li></ul> |
* Samples:
  | sentence_0                                                                                                                                                                                                                                                                                                                                                                                                 | sentence_1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | label            |
  |:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------|
  | <code>Domain: Web Development, Frontend Development, Full Stack. Technical skills: css, html, java, javascript, machine learning, mongodb, natural language processing, node.js, python, react, sql. Experience years: 0.0</code>                                                                                                                                                                          | <code>Job title: Senior Site Reliability Engineer. Company: Ideagen Plc.. Description: Role Purpose<br>Ideagen is the invisible force behind many things we rely on every day - from keeping airplanes soaring in the sky, to ensuring the food on our tables is safe, to helping doctors and nurses care for the sick. So, when you think of Ideagen, think of it as the silent teammate that's always working behind the scenes to help those people who make our lives safer and better.<br>Every day millions of people are kept safe using Ideagen software. We have offices all over the world including America, Australia, Malaysia and India with people doing lots of different and exciting jobs.<br>Ideagen believe that by recruiting diverse and talented individuals, we create an inclusive community for all. We are committed to empowering all colleagues to maximise their potential and express their unique characteristics, experience, and knowledge to achieve their ambitions.<br>Responsibilities<br>• Manage, monitor, and mainta...</code>                | <code>0.0</code> |
  | <code>Domain: Web Development, Frontend Development, Full Stack. Technical skills: bootstrap, css, figma, firebase, git, html, java, javascript, machine learning, material-ui, mongodb, mysql, node.js, os, postman, python, react, tailwind css. Experience years: 0.0</code>                                                                                                                            | <code>Job title: Senior Software Developer (Telecommunications). Company: DCConnect Global. Description: SENIOR SOFTWARE ENGINEER (Telco)<br>JOB DESCRIPTION<br>Develop and maintain our flagship BSS/OSS system for SDN (software defined networking) and SD-WAN (software defined wide area network).<br>Work on cutting-edge SDN products and web portals.<br>Participate in the entire software life-cycle including development, testing and debugging following an agile DevOps model.<br>Research and evaluate the latest software technologies in order to meet user requirements.<br>Write technical documentation for our partners and team members.<br>CORE REQUIREMENTS<br>Higher Diploma or Degree holder in Computer Science or related disciplines, fresh graduates with a passion for software development or computer networks are welcome to apply<br>Highly experienced with Web application development in frontend and backend<br>(TypeScript, Node.js, React, GIT, JSON, CSS, RESTful web services, at least one relational database like MySQL/MariaD...</code> | <code>1.0</code> |
  | <code>Domain: Web Development, Machine Learning / AI, Full Stack. Technical skills: c++, css, deep learning, docker, express.js, firebase, flutter, git, google cloud, html, java, javascript, machine learning, matlab, mongodb, natural language processing, node.js, python, quantum computing, react, ruby, scikit-learn, spring boot, sql, tensorflow, unity, wordpress. Experience years: 0.8</code> | <code>Job title: Senior Java Developer (Microservices). Company: JP Caliber. Description: Requirements<br>5+ years of software development experience in Java 8.<br>Experience in developing microservices using Spring Boot. Experience in security, transaction, Idempotency, log tracing, distributed caching, monitoring, and containerization requirements of microservices. Experience in developing High Cohesion & Loosely Coupled Micro Services.<br>Strong experience in Spring Framework such as Spring Cloud, Spring Boot, Spring Data, Spring Security, Spring Batch, Spring AOP and others. Extensive experience in developing Microservices using Netflix OSS (Zuul, Eureka, Ribbon, Hystrix), Feign Client, Sleuth and Zipkin.<br>Working experience in Industry Standard protocols related to API Security including OAuth.<br>Should have excellent acumen in Data Structures, algorithms, problem-solving and Logical/Analytical skills. Thorough understanding of OOPS concepts, Design principles and implementation of different types ...</code>                | <code>1.0</code> |
* Loss: [<code>BinaryCrossEntropyLoss</code>](https://sbert.net/docs/package_reference/cross_encoder/losses.html#binarycrossentropyloss) with these parameters:
  ```json
  {
      "activation_fn": "torch.nn.modules.linear.Identity",
      "pos_weight": null
  }
  ```

### Training Hyperparameters
#### Non-Default Hyperparameters

- `per_device_train_batch_size`: 32
- `num_train_epochs`: 2
- `per_device_eval_batch_size`: 32

#### All Hyperparameters
<details><summary>Click to expand</summary>

- `per_device_train_batch_size`: 32
- `num_train_epochs`: 2
- `max_steps`: -1
- `learning_rate`: 5e-05
- `lr_scheduler_type`: linear
- `lr_scheduler_kwargs`: None
- `warmup_steps`: 0
- `optim`: adamw_torch_fused
- `optim_args`: None
- `weight_decay`: 0.0
- `adam_beta1`: 0.9
- `adam_beta2`: 0.999
- `adam_epsilon`: 1e-08
- `optim_target_modules`: None
- `gradient_accumulation_steps`: 1
- `average_tokens_across_devices`: True
- `max_grad_norm`: 1
- `label_smoothing_factor`: 0.0
- `bf16`: False
- `fp16`: False
- `bf16_full_eval`: False
- `fp16_full_eval`: False
- `tf32`: None
- `gradient_checkpointing`: False
- `gradient_checkpointing_kwargs`: None
- `torch_compile`: False
- `torch_compile_backend`: None
- `torch_compile_mode`: None
- `use_liger_kernel`: False
- `liger_kernel_config`: None
- `use_cache`: False
- `neftune_noise_alpha`: None
- `torch_empty_cache_steps`: None
- `auto_find_batch_size`: False
- `log_on_each_node`: True
- `logging_nan_inf_filter`: True
- `include_num_input_tokens_seen`: no
- `log_level`: passive
- `log_level_replica`: warning
- `disable_tqdm`: False
- `project`: huggingface
- `trackio_space_id`: None
- `trackio_bucket_id`: None
- `trackio_static_space_id`: None
- `per_device_eval_batch_size`: 32
- `prediction_loss_only`: True
- `eval_on_start`: False
- `eval_do_concat_batches`: True
- `eval_use_gather_object`: False
- `eval_accumulation_steps`: None
- `include_for_metrics`: []
- `batch_eval_metrics`: False
- `save_only_model`: False
- `save_on_each_node`: False
- `enable_jit_checkpoint`: False
- `push_to_hub`: False
- `hub_private_repo`: None
- `hub_model_id`: None
- `hub_strategy`: every_save
- `hub_always_push`: False
- `hub_revision`: None
- `load_best_model_at_end`: False
- `ignore_data_skip`: False
- `restore_callback_states_from_checkpoint`: False
- `full_determinism`: False
- `seed`: 42
- `data_seed`: None
- `use_cpu`: False
- `accelerator_config`: {'split_batches': False, 'dispatch_batches': None, 'even_batches': True, 'use_seedable_sampler': True, 'non_blocking': False, 'gradient_accumulation_kwargs': None}
- `parallelism_config`: None
- `dataloader_drop_last`: False
- `dataloader_num_workers`: 0
- `dataloader_pin_memory`: True
- `dataloader_persistent_workers`: False
- `dataloader_prefetch_factor`: None
- `remove_unused_columns`: True
- `label_names`: None
- `train_sampling_strategy`: random
- `length_column_name`: length
- `ddp_find_unused_parameters`: None
- `ddp_bucket_cap_mb`: None
- `ddp_broadcast_buffers`: False
- `ddp_static_graph`: None
- `ddp_backend`: None
- `ddp_timeout`: 1800
- `fsdp`: None
- `fsdp_config`: None
- `deepspeed`: None
- `debug`: []
- `skip_memory_metrics`: True
- `do_predict`: False
- `resume_from_checkpoint`: None
- `warmup_ratio`: None
- `local_rank`: -1
- `prompts`: None
- `batch_sampler`: batch_sampler
- `multi_dataset_batch_sampler`: proportional
- `router_mapping`: {}
- `learning_rate_mapping`: {}

</details>

### Training Logs
| Epoch  | Step | Training Loss |
|:------:|:----:|:-------------:|
| 0.9058 | 500  | 0.4273        |
| 1.8116 | 1000 | 0.2083        |


### Training Time
- **Training**: 48.3 minutes

### Framework Versions
- Python: 3.12.13
- Sentence Transformers: 5.6.0
- Transformers: 5.13.1
- PyTorch: 2.11.0+cu128
- Accelerate: 1.14.0
- Datasets: 4.0.0
- Tokenizers: 0.22.2

## Additional Resources

- [Training and Finetuning Reranker Models with Sentence Transformers](https://huggingface.co/blog/train-reranker): the end-to-end guide for training or finetuning Cross Encoder (reranker) models.
- [Multimodal Embedding & Reranker Models with Sentence Transformers](https://huggingface.co/blog/multimodal-sentence-transformers): use text, image, audio, and video reranker models through the same API.
- [Training and Finetuning Multimodal Embedding & Reranker Models with Sentence Transformers](https://huggingface.co/blog/train-multimodal-sentence-transformers): training multimodal Cross Encoders.

## Citation

### BibTeX

#### Sentence Transformers
```bibtex
@inproceedings{reimers-2019-sentence-bert,
    title = "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks",
    author = "Reimers, Nils and Gurevych, Iryna",
    booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing",
    month = "11",
    year = "2019",
    publisher = "Association for Computational Linguistics",
    url = "https://arxiv.org/abs/1908.10084",
}
```

<!--
## Glossary

*Clearly define terms in order to be accessible across audiences.*
-->

<!--
## Model Card Authors

*Lists the people who create the model card, providing recognition and accountability for the detailed work that goes into its construction.*
-->

<!--
## Model Card Contact

*Provides a way for people who have updates to the Model Card, suggestions, or questions, to contact the Model Card authors.*
-->