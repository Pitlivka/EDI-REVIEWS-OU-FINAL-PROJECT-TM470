# EDI REVIEWS
TM470-project-public EMA version without API URL
Review app created with Python, SQL and KIVY GUI framework.
# Description: 
The lack of information on discriminatory practices at certain locations can put people from minority groups in uncomfortable and potentially dangerous situations. While there are review platforms available, they do not always provide specific details that are relevant to these groups. An anti-discrimination review application, specifically designed for people who belong to the minorities, could make a significant contribution towards inclusivity, diversity, and safety for all. By enabling users to submit and read reviews relevant to them, the proposed "EDI-Reviews" application could provide a much-needed solution to this issue. EDI in the name stands for the Equality, diversity, and inclusion.

The application will also provide accessibility features to make it user-friendly for everyone, while a reporting system will allow users to report suspicious reviews, therefore ensuring that the application is used responsibly. Data collected through the application could also be used to raise awareness with the government, potentially leading to positive changes for the  minorities.
Currently available review platforms such as TripAdvisor and Google Reviews lack the necessary features to filter reviews based on specific search terms. As a result, searches for words such as "homophobic" or "xenophobic" often return no results. The "EDI Review" application would fill this gap by allowing users to submit reviews that are specifically relevant to people who belong to minority groups.

Overall, the proposed "EDI-Review" application has the potential to create a safer and more inclusive society by promoting diversity and inclusivity and creating a platform for minorities to make informed decisions.

The app developed using iterative and incremental development methodology based on Scrum agile method. I will act as the user and developer, setting requirements and testing them myself. PyCharm and Python will be used for development, and the data will be saved in a MySQL local database server. GEO location API by LocationIq will be used for venue search.
The GUI is developed with KIVI, and the app will be deployed for Android OS. Every search location will be saved to the database with its specific ID tag and other information provided during review submission. 


# Images showing the app executed in PyCharm:

![image](https://github.com/Pitlivka/finall-roject-public/assets/88449521/4f903732-029d-4e10-8d30-59d77cc77817)


![image](https://github.com/Pitlivka/finall-roject-public/assets/88449521/632e6c39-dc17-41f6-a82f-8c8c9546c5fd)


![image](https://github.com/Pitlivka/finall-roject-public/assets/88449521/3d4010a2-60fe-4f29-bec4-12abdc425dba)


![image](https://github.com/Pitlivka/finall-roject-public/assets/88449521/caf57029-9066-4387-be25-951508e9e8f2)


![image](https://github.com/Pitlivka/finall-roject-public/assets/88449521/0ad4c7fd-62d3-43a6-b0a2-47a9f6ce8e5a)


Unfortunatelly I was unabble to deploy the app to Android due to compatibility issues between KIVI and C language.
The Buildozer tool which supposes to package the mobbile applications is failing to create the .apk file.
I have not been able to find the solution to this problem yet and I am not sure what is the issue.
