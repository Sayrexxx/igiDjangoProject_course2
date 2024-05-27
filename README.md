This project is a tutorial assignment for the IGI subject of the 2nd year of the IITP/FCSIS BSUIR specialty.  
This repository contains a project on Django framework, which is a backend for an application called 
## "Toy Factory"

Use the following instructions to launch the application:

Create an image:  
`docker build -t <your_image_name> .`  
  
(for example: `docker build -t igi_image .`  , your_image_name must be in lower case, special characters are allowed)

Create and run the container with the application:  
`docker run --name <your_container_name> -dp <your_ports> <your_image_name>`  
  
(for example: `docker run --name igi_container -dp 8000:8000 igi_image`)  

###### Tests are run during the image creation phase

### localhost:<your_output_port>   

to see application

### localhost:8000 (for example)
