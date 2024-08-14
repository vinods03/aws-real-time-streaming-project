Please refer the "Architecture Diagram.pptx" first.
This ETL pipeline on AWS is designed for continuous workloads. So using non-serverless components (EMR). Any data discrepancy between the layers is also captured in real time.
Serverless components (like Glue) are better-suited and more cost-effective for adhoc / variable workloads.
