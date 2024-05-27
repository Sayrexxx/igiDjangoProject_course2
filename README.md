This project is a tutorial assignment for the PGI subject of the 2nd year of the IITP FKSIS BSUIR specialty. 
This repository contains a project on Django framework, which is a backend for an application called 
## "Toy Factory"

Use the following instructions to launch the application:

Create an image: 
`docker build -t <your_image_name> .`
(for example: `docker build -t igi .`  , your_image_name must be in lower case, special characters are allowed)

Create and run the container with the application:
`docker run -dp <your_ports> <your_image_name>`
(for example: `docker run -dp 8000:8000 igi`)


Tests are run during the image creation phase
