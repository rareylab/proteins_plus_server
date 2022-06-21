ProteinsPlus Developer Guide
===========================
Before you submit any changes to the server's codebase make sure to first review the following
guidelines and the tutorial below.

# Table of Contents

[//]: # "Note that some Markdown engines are not able to make the TOC clickable"

---

- [Guidelines](#guidelines)
    - [Code Quality](#code-quality)
    - [Documentation](#documentation)
    - [Database Consistency](#database-consistency)

- [Tutorial](#tutorial)
    - [Project Structure](#project-structure)
    - [Starting the Server](#starting-the-Server)
    - [Creating a new App](#creating-a-new-app)
    - [Testing](#testing)
    - [Models](#models)
        - [Output Models](#output-models)
        - [Input Models and Caching](#input-models-and-caching)
        - [Job Models](#Job-models)
        - [Models and Cascading Deletion](#models-and-cascading-deletion)
        - [Models and File Handling](#models-and-file-handling)
    - [Serializers](#serializers)
        - [Model Serializer](#model-serializer)
        - [Job Retrieval Serializers](#job-retrieval-serializers)
        - [Job Submission Serializer](#job-submission-serializer)
    - [Views](#views)
        - [Retrieve and List View](#retrieve-and-list-view)
        - [Job Submission Views](#job-submission-views)
    - [Urls](#urls)
    - [Tasks](#tasks)
    - [Tool Wrapper](#tool-wrapper)
    - [Caching](#caching)
- [Deployment](#deployment)
    - [Start and Stop](#start-and-stop)
        - [Redis](#redis)
        - [Celery](#celery)
        - [Gunicorn](#gunicorn)
        - [Display Server](#display-server)
    - [Clean](#clean)

---

# Guidelines

## Code Quality

Contributions to the project must comply to the following quality criteria to keep the code
maintainable for all developers:

| Criteria               | Threshold |
|------------------------|:---------:|
| pylint                 |   \>9.0   |
| coverage (overall)     |   \>90%   |
| coverage (single file) |   \>80%   |

Run pylint for static code quality check with

```bash
find . -type f -name "*.py" | xargs pylint --load-plugins pylint_django --django-settings-module=proteins_plus.settings
```

Run test coverage

```bash
coverage run manage.py test <path_to_app>
coverage report
```

## Documentation

Every file, class or function must be documented using the
[Sphinx docstring style](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html).

## Database Consistency

To ensure that the database is always consistent, you must not store invalid or empty objects in
the database. Neither should you change existing objects. All objects except jobs are considered
immutable. The following list of scenarios is not complete but gives an overview over the most
common situations where this is important:

- Only save an object to the database, if it is valid.
- Only create a job object, if all input objects are created and saved to the database.
- When creating a job model, make sure the output models references can be None.
- Do not create empty output objects for a job before it has been run. Just submit the job without
  any output objects assigned.
- Only create output objects after a job execution has finished successfully and the output data
  was validated. First create the valid output object, save it to the database and then assign it
  to the job object.
- Never overwrite or change any of a program's input objects. Always create new output objects for
  any output of your program.
- Do not delete objects from the database if this results in empty or faulty references in any
  other database objects.

# Tutorial

This guide explains how to integrate new tools into the ProteinsPlus server. The server is built
with Django and the Django REST framework. We highly advise familiarizing yourself with these
packages before changing anything. Documentation and tutorials can be found here:

- Django: https://www.djangoproject.com/
- Django REST framework: https://www.django-rest-framework.org/

If you haven't already you should now install
[conda](https://docs.conda.io/en/latest/miniconda.html) and set up the pplus environment:

```bash
conda env create -f environment.yml
conda activate pplus
```

## Project Structure

First let's have a look at the project structure. You should use this as a reference when building
your own apps or when you are unsure where to find existing code.

```
.
├── README.md                               # General Information.
│
├── Developer-Guide.md                      # Development guidelines and instructions.
│
├── bin                                     # Directory for all binaries.
│   └── <toolname>                          # Subdirectory for your tool's executable files.
│
├── environment.yml                         # A File that lists all dependecies to ensure seamless
│                                           # environment creation.
│                                           # New packages might be added here. However, we are very
│                                           # restrictive with new packages to keep the project
│                                           # lean and easy to maintain. If possible use conda
│                                           # instead of pip.
│
├── manage.py                               # Main python file to interact with the server.
│
├── media                                   # Directory for all files. If your tool creates
│                                           # persistent files they should be saved to an
│                                           # appropriate subdirectory.
│
├── molecule_handler                        # Central app for molecule handling.
│
├── proteins_plus                           # Core project app. Do not change anything here without
│   │                                       # explicit need and permission.
│   ├── apps.py                             # Internal Django file.
│   ├── asgi.py                             # Internal Django file.
│   ├── binaries.json                       # JSON containing the paths of all binaries.
│   ├── celery.py                           # Celery setup file.
│   ├── job_handler.py                      # Contains necessary functions for job interaction.
│   ├── models.py                           # Contains Django base models for the whole project.
│   ├── serializers.py                      # Contains serializers for the base models.
│   ├── settings.py                         # All server settings are controlled from here. This
│   │                                       # file also contains common constants like important
│   │                                       # directory paths and frequently used urls.
│   ├── test                                # A submodule for unit tests.
│   │   └── utils.py                        # A file containing global convenience functions for 
│   │                                       # testing.
│   ├── urls.py                             # All central API routing is controlled from here.
│   └── wsgi.py                             # Internal Django file.
│
├── test_files                              # Directory for all files that are used in unit tests.
│
├── templates                               # Directory containing usefull template files for new
│                                           # apps.
│
└── <toolname>                              # Example app.
    ├── __init__.py                         # Necessary file. May be empty.
    ├── admin.py                            # File for handling display on the admin page.
    ├── apps.py                             # Internal Django file.
    ├── migrations                          # Subdirectory for all database migrations. Do not
    │                                       # change anything here manually.
    ├── models.py                           # This file contains all Django models.
    ├── serializers.py                      # This file contains serializers for the models.
    ├── tasks.py                            # This file is the interface between the views and the 
    │                                       # <toolname>_wrapper. It should contain Celery tasks
    │                                       # that call the appropriate function from the 
    │                                       # <toolname>_wrapper to invoke execution of the tool.
    ├── test                                # A submodule for unit tests.
    │   ├── __init__.py                     # Necessary file. It has to import all files with test
    │   │                                   # cases.
    │   ├── config.py                       # A file to configure the test cases. Should contain
    │   │                                   # paths and filenames of any testfiles. 
    │   ├── model_tests.py                  # Contains all test cases for the models.
    │   ├── task_tests.py                   # Contains all test cases for the tasks.
    │   ├── util_tests.py                   # Contains all test cases for the utility functions.
    │   ├── utils.py                        # Contains utility functions for the test cases such as
    │   │                                   # dummy job creation.
    │   └── view_tests.py                   # Contains all test cases for the views.
    ├── <toolname>_wrapper.py               # Contains the workflow for the tool's execution.
    ├── urls.py                             # Contains all internal api routes.
    └── views.py                            # Contains all views. All interactions with the user
                                            # happen here.
```

## Starting the Server

There are a few commands you need to execute to get the server running. Make sure you have
activated your conda environment with:

```bash
conda activate pplus
```

Open a separate terminal and start the redis server. This is needed by celery which we use for
distributed task execution.

```bash
redis-server --port 6378
```

Open another separate terminal and start the celery worker.

```bash
celery -A proteins_plus worker -O fair --loglevel=INFO
```

Migrate pending changes to the database. You need to repeat this step whenever you have made any
changes to the project's database **Models**.

```bash
python manage.py makemigrations
python manage.py migrate
```

To start the server run:

```bash
python manage.py runserver
```

Now the server is running at http://localhost:8000/.

You can see the interactive Swagger API at http://localhost:8000/api/schema/swagger-ui. This is a
great way to see the server's capabilities and quickly test its behaviour when implementing new
functionalities. We recommend you to play around with this API for a bit to get familiar with the
project. To generate or regenerate the API description execute the following:

```bash
python manage.py spectacular --file schema.yml
```

## Creating a new App

To integrate a tool into the workflow you first have to create an app. The name of your app should
be the name of the tool to be integrated. Use lowercase letters and underscores as spaces if
necessary.

```bash
python manage.py startapp your_app
```

For Django to recognize the app, you need to add it to the list of installed apps inside the
**proteins_plus/settings.py** file:

```python
# proteins_plus/settings.py

...
# Application definition

INSTALLED_APPS = [
    ...
    'your_app.apps.your_app_config',  # You can look up the name of your_app_config inside the your_app/apps.py file.
]
...
```

Next, you need to make your app accessible through the server's API. Open the
**proteins_plus/urls.py** file and add the following code:

```python
# proteins_plus/urls.py

...
urlpatterns = [
    ...
    path('your_app/', include('your_app.urls'))
]
...
```

## Testing

While you are adding code to the server it is important to make sure everything works as intended.
Therefore, you have to write unit tests for every component that you build. Instead of a single
test script, which Django automatically creates for you, this project uses a different, more
organized and scalable approach by adding a dedicated testing module to every app. As you can see
in the project structure above, you should remove the **your_app/tests.py** file and replace it
with a new directory named **your_app/test/**. Inside this directory, you should create the
following files:

1. **model_tests.py**: In this file you will create all test cases for your models.
2. **view_tests.py**: In this file you will create all test cases for your views.
3. **task_tests.py**: In this file you will create all test cases for your task and the correct
   execution of your program.
4. **\_\_init\_\_.py**: In this file you need to import the **TestCase** class from each of the
   other files. Apart from that, this file can be empty.
5. **config.py**: In this file you can define useful constants like paths to test files that your
   other test cases use.
6. **util_tests.py**: This file is not always needed. You can create and use it to test specific
   functions throughout your whole app that don't fit well into one of the other test files.
7. **utils.py**: This file is also optional. You can create it to define helper functions that ease
   some processes in the test cases and reduce redundancy. An example would be the creation of
   dummy database objects, that you need to test your workflow. Keep in mind that this file must
   not contain any functions that are required for the regular operation of your app as it is only
   intended to ease the testing procedure.

Make sure you do not only test for the intended behaviour of a user but also check for edge cases.
If you need more general information about testing, refer to the official Django
[Documentation](https://docs.djangoproject.com/en/4.0/topics/testing/overview/).

You can execute your tests with the following command:

```bash
python manage.py test <path_to_your_app>        # Only run unit tests for your application
python manage.py test                           # Run all unit tests
```

## Models

Now let's start coding. To store data in the database you need to create Django **Models**.
**Models** are stored inside the **your_app/models.py** file. The following explanations assume
that you have basic knowledge about how Django **Models** work. If you require additional
information refer to the official Django
[Documentation](https://docs.djangoproject.com/en/4.0/topics/db/models/). There are three main
types of **Models** that you will build for your app.

### Output Models

If your tool produces some kind of output data that should be stored in the database you should
create a Django **Model** for it. Use the **ProteinsPlusBaseModel** as base for your class and add
all necessary **Fields** with appropriate datatypes like this:

```python
# your_app/models.py
from django.db import models

from proteins_plus.models import ProteinsPlusBaseModel

...
class YourOutputModel(ProteinsPlusBaseModel):
    """Description"""
    field1 = models.CharField(...)
    ...
...
```

### Input Models and Caching

If your tool requires additional input data that should be stored in the database you should
create a Django **Model** for it. Use the **ProteinsPlusHashableModel** as base for your class.
This base class provides the necessary infrastructure for your model to be compatible with the
caching engine. This ensures that jobs with identical input parameters are only executed once. To
enable the caching workflow you need to add an additional variable to the class named
`hash_attributes`. In this variable you need to store a list containing all attributes by name that
are required to uniquely identify a specific **Model** instance. During caching, two objects are
compared by these attributes and are considered identical if and only if all values of the given
attributes are equal. These attributes can include common Django **Field** types such as
**CharField**, **FloatField** or even **FileField**. It is also possible to name reference
attributes such as **ForeignKey** as long as the referenced **Model** inherits from the
**ProteinsPlusHashableModel** base Model. Typical **Fields** that you would not include in the
`hash_attributes` list include meta information such as the date of creation of an object. You can
find out more about how caching works in the dedicated paragraph below. Your input **Model**
definition could look like this:

```python
# your_app/models.py
from django.db import models

from proteins_plus.models import ProteinsPlusHashableModel
from molecule_handler.models import Protein

...
class YourInputModel(ProteinsPlusHashableModel):
    """Description"""
    field1 = models.ForeignKey(Protein, ...)
    field2 = models.FloatField(...)
    field3 = models.FileField(...)
    some_meta_information = models.CharField(...)
    ...

    hash_attributes = ['field1', 'field2', 'field3']
...
```

### Interoperability

A few generally useful **Models** are provided in the **molecule_handler**. The
**molecule_handler** and **proteins_plus** apps are the only one you should be importing
functionality and models from. The models in **molecule_handler** are of common types of data that
a number of **apps** can use as input **Models** and output **Models**. This means that the output from
one **app** can be used as the input for another **app**. It also means that the **Models**
lifetime is not necessarily controlled by just one **app**. For that reason **molecule_handler**
contains a cleanup mechanism. If you do end up implementing a new interoperable **Model** type
it should be implemented in **molecule_handler** and integrated into the cleanup mechanism.

### Job Models

Finally, you will need to create a Django **Model** representing a job. A **Job Model** contains
all information that is required to execute your tool. It references all input and output objects
that are produced by your tool. The base class for all jobs is **ProteinsPlusJob**.
**ProteinsPlusJob** inherits from the **ProteinsPlusHashableModel** base class. It is therefore
itself hashable and needs the `hash_attributes` variables. For jobs, only the input **Models**
should be included in the `hash_attributes` list. A typical **Job Model** looks like this:

```python
# your_app/models.py
from django.db import models

from proteins_plus.models import ProteinsPlusJob
from molecule_handler.models import Protein

...
class YourJob(ProteinsPlusJob):
    """Description"""
    input_field1 = models.ForeignKey(Protein, ...)
    input_field2 = models.OneToOneField(YourInputModel, ...)
    output_field = models.OneToOneField(YourOutputModel, ...)
    some_meta_information = models.CharField(...)
    ...

    hash_attributes = ['input_field1', 'input_field2']
...
```

### Models and Cascading Deletion

Django provides cascading deletion for database models (`on_delete=models.CASCADE`). Models that
have no reason to exist when other models related to them are deleted, should also be deleted using
this mechanism. Make sure to familiarize yourself with cascading deletion using the official django
[documentation](https://docs.djangoproject.com/en/4.0/topics/db/models/). Cascading deletion should
be tested and documented in **model_tests**.

In general:

1. Job models should be deleted if any of their input or output has been deleted
2. Job input models should be deleted if their job was deleted, and they cannot be used as input for
   another job
3. Job output models should be deleted if their job was deleted, and they cannot be used as input
   for another job

Points 2. and 3. are usually valid for any model you have defined yourself. Note that you should
not be importing models from other apps except for **molecule_handler**. Models such as
**molecule_handler.models.Protein** or **molecule_handler.models.Ligand** are some of the few
models that should not be deleted when a job model they are used in is deleted.

### Models and File Handling

One thing to keep in mind when building new **Models** is file handling. If a **Model** definition
contains a **FileField** you need to specify a directory where these files should be stored. Files
should be placed in an appropriate subdirectory inside the **media/** directory. If you create a
new subdirectory make sure to include its path in the `MEDIA_DIRECTORIES` dictionary inside the
**proteins_plus/settings.py** file and always use this reference when using the path in your app.
Do not use any hard coded paths inside your code.

Another thing to consider here is the deletion of files. Files are only allowed to exist if there
is a valid database object referencing it. This policy is necessary to avoid accumulation of unused
files. To ensure this behavior you need to delete any files that are referenced by a database
object before it is deleted. This can be achieved with the **django.dispatch.dispatcherreceiver**
decorator. Include this for every model that uses a **FileField**. See an example below:

```python
# your_app/models.py
from django.db import models
from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

from proteins_plus.models import ProteinsPlusBaseModel

...
class YourModel(ProteinsPlusBaseModel):
    """Description"""
    some_file = models.FileField(upload_to=settings.MEDIA_DIRECTORIES['your_subdirectory'], ...)
    ...
...
@receiver(pre_delete, sender=YourModel)
def some_file_delete(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """Description"""
    instance.some_file.delete(False)
...
```

The last thing to mention here is the assignment of files to a **FileField**. This task is somewhat
unintuitive as you have to make sure that the file you are assigning is copied to the intended
directory. You can refer to the following code snippet whenever you create an object with a file
reference:

```python
# your_app/some_file.py
from django.core.files import File
from your_app.models import YourModel

...
your_file_path = 'path/to/file'  # E.g. this could be an output file of your program
your_new_object = YourModel(...)  # Do not set the FileField in the constructor
your_new_object.some_file.save('new_file_name', File(open(your_file_path, 'rb')))
your_new_object.save()
```

## Serializers

**Serializers** are a concept introduced by the Django REST Framework. They are used to specify how
instances of a given **Model** should be transferred from and to the user and which **Fields**
should be included. The **Serializers** should be defined inside the **your_app/serializers.py**
file. This file needs to be created manually. Again, the following explanations assume that you are
familiar with **Serializers** in general. If you require more information refer to the official
[Documentation](https://www.django-rest-framework.org/api-guide/serializers/).

### Model Serializer

To define a **Serializer** for a basic **Model** you need to inherit the base **Serializer** from
the Django REST Framework and add all fields that should be communicated with the user to the
`fields` list like this:

```python
# your_app/serializers.py
from rest_framework import serializers
from .models import YourModel

...
class YourModelSerializer(serializers.ModelSerializer):
    """Description"""

    class Meta:
        model = YourModel
        fields = ['id', 'field1', 'field2']
        ...
...
```

### Job Retrieval Serializers

To define a **Serializer** for the retrieval of a **ProteinsPlusJob** instance, you need to
implement the **ProteinsPlusJobSerializer** base class and adopt the already existing fields. You
can do this by only appending to instead of overwriting the `fields` list. An example looks like
this:

```python
# your_app/serializers.py
from proteins_plus.serializers import ProteinsPlusJobSerializer
from .models import YourJob

...
class YourJobSerializer(ProteinsPlusJobSerializer):
    """Description"""

    class Meta(ProteinsPlusJobSerializer.Meta):
        model = YourJob
        fields = ProteinsPlusJobSerializer.Meta.fields + [
            'input_field1',
            'input_field2',
            'output_field',
            'some_meta_information'
        ]
...
```

### Job Submission Serializer

To handle the submission of a job you need to implement a submission **Serializer**. This
**Serializer** represents the information that a user needs to provide in order to execute a job.
The given information will be processed and converted into the final input **Model** instances that
are required by the job **Model**. Therefore, the **Serializer** **Fields** will not match the job
**Model** **Fields** in most cases. Instead, you have to ensure that the job **Model** **Fields**
can be inferred from the **Serializer** **Fields**.

To build a submission **Serializer** you first need to implement the
**ProteinsPlusJobSubmitSerializer** base class. Then you add your **Fields** just like you would
when creating a **Model**. Note that in this case you use the **Fields** from
**rest_framework.serializers** instead of **django.db.models**. Finally, you should overwrite a
function named **validate**. In this function you have access to the data submitted by the user
through the function's only parameter which is a dictionary. The dictionary's keys are the
attribute names. Inside the **validate** function, you should perform any data validation steps
that are necessary to ensure a successful job execution. In case of any error in the data you
should raise a **rest_framework.serializers.ValidationError** or another appropriate exception. If
the data fulfills all criteria you need to return the data object. An example submission
**Serializer** looks like this:

```python
# your_app/serializers.py
from rest_framework import serializers
from proteins_plus.serializers import ProteinsPlusJobSubmitSerializer
from molecule_handler.input_validation import MoleculeInputValidator

...
class YourSubmitSerializer(ProteinsPlusJobSubmitSerializer):  # pylint: disable=abstract-method
    """Description"""
    protein_id = serializers.UUIDField(required=True)
    pdb_code = serializers.CharField(min_length=4, max_length=4, default=None)

    def validate(self, data):  # pylint: disable=arguments-renamed
        """Description"""

        # For molecule input, like protein/ligand/density files or PDB/Uniprot codes
        #   we use the standardized MoleculeInputValidator instead of checking
        #   data['pdb_code'] manually. Note however, non-molecule input, you have
        #   to validate yourself by examining data['your_parameter'] here.
        validator = MoleculeInputValidator(data)
        if not validator.has_valid_pdb_code() and not validator.has_valid_protein_file():
            raise serializers.ValidationError('Neither pdb code not pdb file were provided.')
        return data
...
```

## Views

The **Views** represent the bridge between the user and the database. Through the **Views** a user
can retrieve objects from the database or execute tools to generate new data. Again, the following
explanations assume that you are familiar with **Views** and **ViewSets** in general. If you
require more information refer to the official Documentation. There are two important types of
**Views** you need to know.

### Retrieve and List View

These **Views** are used to retrieve specific or listing all **Model** instances in the database.
To implement such a **View** your class needs to inherit from the **ReadOnlyModelViewSet**, specify
a `queryset` from which objects should be retrieved and a `serializer_class` that should be used to
package the data. Below is an example:

```python
# your_app/views.py
from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import YourModel
from .serializers import YourModelSerializer

...
class YourModelViewSet(ReadOnlyModelViewSet):  # pylint: disable=too-many-ancestors
    """Description"""
    queryset = YourModel.objects.all()
    serializer_class = YourModelSerializer
...
```

### Job Submission Views

These **Views** define the workflow of submitting a job. In these **Views** you preprocess the user
submitted data and create the necessary input **Model** instances. There are a couple of things to
consider when writing these **Views**. First, if your view should support file upload, you need to
add the **MultiPartParser** and **FormParser** classes to a field named `parser_classes` at the
beginning of the class definition. Next, for the Swagger API to work you need to specify request
and response **Serializer** classes that should be used. You need to do this inside an
`extend_schema` decorator. The HTTP method used for the **View** should be POST, since a user
introduces new data to the database. Inside the **View** you then build the submission workflow.
First you need to extract the user data and ensure that it is valid. Then, you create the input
**Model** instances and a job object. Create only the input objects and not the output objects as
those are created after your tool's execution. Submit a task for the job execution and return the
response data to the user. This response data will include the freshly created job's id and a flag
indicating whether the result was retrieved from the cache. The user can use the job id to later
retrieve the job from the database and check its status. An example **View** is given below:

```python
# your_app/views.py
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema

from proteins_plus.serializers import ProteinsPlusJobResponseSerializer
from proteins_plus.job_handler import submit_task

from .models import SomeModel, YourJob
from .tasks import your_task

...
class YourJobSubmissionView(APIView):
    """Description"""
    parser_classes = (MultiPartParser, FormParser)  # required for file upload

    @extend_schema(  # required for Swagger API
        request=YourSubmitSerializer,
        responses=ProteinsPlusJobResponseSerializer,
    )
    def post(self, request):
        """Description"""
        # Use your serializer to ensure data validation
        serializer = YourSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # this calls your validate function
        request_data = serializer.validated_data

        # Extract user data
        some_object_id = request_data['some_object_id']
        some_parameter = request_data['some_parameter']

        # Process and convert user data
        some_object = SomeModel.objects.get(id=some_object_id)

        # Create job object with input objects
        job = YourJob(
            some_object=some_object,
            some_parameter=some_parameter
        )

        # Submit job for execution
        # Note that the ProteinsPlusJobSubmitSerializer used as base class for the request
        # serializer ensures that the request_data contains a field named 'use_cache', which the
        # user can use to manually disable the cache for a request.
        response_data = submit_task(job, your_task, request_data['use_cache'])

        # Return response to the user
        serializer = ProteinsPlusJobResponseSerializer(response_data)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
...
```

## Urls

To make your **Views** accessible to the user you need to integrate them into the API. The two
types of **Views** require two different methods for this. First, create a file named
**your_app/urls.py**. The routes for the submission **Views** are directly added to a list named
`url_patterns`. The **ViewSets** need to be registered by a **Router**. See the example below:

```python
# your_app/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from your_app import views

urlpatterns = [
    path('your_tool/', views.YourJobSubmissionView.as_view()),
    ...
]

router = DefaultRouter()
router.register('your_model', views.YourModelViewSet)
router.register('your_tool/jobs', views.YourJobViewSet)
...
urlpatterns.extend(router.urls)
```

These **Views** will then be accessible at

- https://localhost:8000/your_app/your_tool/
- https://localhost:8000/your_app/your_model/
- https://localhost:8000/your_app/your_tool/jobs/

You can quickly verify this behaviour by checking the interactive Swagger UI at
http://localhost:8000/api/schema/swagger-ui.

## Tasks

As described in the **Views** section, you submit your job as a task for execution. You define this
task inside a new file named **your_app/tasks.py**. Inside this file you need to create two
functions. The task function is decorated by the Celery `shared_task` decorator. The function
itself is only a placeholder to call the **proteins_plus.job_handler.execute_job** function. It
handles some infrastructure surrounding the job execution such as updating the job's status. As a
parameter it takes a callback function which is the second function you need to define inside the
**your_app/tasks.py** file. The callback function performs any last preprocessing steps with the
input data before your tool's binary is called. The binary execution happens inside the
**your_app/your_tool_wrapper.py** file. See the example below:

```python
# your_app/tasks.py
import requests
from celery import shared_task
from django.conf import settings
from proteins_plus.job_handler import execute_job
from .your_tool_wrapper import YourToolWrapper
from .models import YourJob


@shared_task
def your_task(job_id):
    """Description"""
    execute_job(your_callback_function, job_id, YourJob, 'your_tool')


def your_callback_function(job):
    """Description"""
    # Example of retrieving a pdb file from the pdb database
    url = f'{settings.URLS["pdb_files"]}{job.pdb_code}.pdb'
    req = requests.get(url)
    if req.status_code != 200:
        raise RuntimeError(
            f"Error while retrieving pdb file with pdb code {job.pdb_code}\n" +
            f"Request: GET {url}\n" +
            f"Response: \n{req.text}"
        )
    job.protein_string = req.text

    # Call your tool's wrapper
    YourToolWrapper.your_tool(job)
```

## Tool Wrapper

After all necessary input is provided, you can implement the execution of your tool inside a new
file named **your_app/your_tool_wrapper.py**. A typical workflow for this procedure includes
creating a temporary dictionary for your output files, executing the binary, processing the
produced output files to create new database objects and assigning them to the original job object.
Make sure to instantiate the output models only after the program has finished and an output was
actually produced, so you don't create empty or faulty objects. It is also important to never
overwrite any of the input objects. All objects except jobs are regarded as immutable and should
only be created if consistency can be guaranteed. You should register the path to your tool in
`proteins_plus/binaries.json` and make sure it is available to the testing pipeline. An example
workflow is given below:

```python
# your_app/your_tool_wrapper.py
import logging
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from django.conf import settings

from .models import YourModel

logger = logging.getLogger(__name__)


class YourToolWrapper:
    """Description"""

    @staticmethod
    def your_tool(job):
        """Description"""
        with TemporaryDirectory() as directory:
            dir_path = Path(directory)
            YourToolWrapper.execute_your_tool(job, dir_path)
            YourToolWrapper.load_results(job, dir_path)

    @staticmethod
    def execute_your_tool(job, directory):
        """Description"""
        args = [
            settings.BINARIES['your_tool'],
            '--other_parameter', job.some_parameter,
            '--outdir', str(directory.absolute()),
        ]

        logger.info('Executing command line call: %s', " ".join(args))
        subprocess.check_call(args)

    @staticmethod
    def load_results(job, path):
        """Description"""
        PreprocessorWrapper.load_protein(job, path)
        ...  # Load other results
        job.save()

    @staticmethod
    def load_protein(job, path):
        """Description"""
        pdb_files = list(path.glob('*.pdb'))
        with pdb_files[0].open() as pdb_file:
            pdb_string = pdb_file.read()
        job.output_protein = Protein(
            name='some_name',
            file_type='pdb',
            file_string=pdb_string
        )
        job.output_protein.save()
```

## Caching

The caching system is designed to avoid redundant execution of identical jobs on the server. The
mechanism used to achieve this goal is simple. When a job is submitted through the provided
**proteins_plus.job_handler.submit_task** function, a hash key is built for the job object. This is
done by first hashing the job's hash attributes given by it's `hash_attributes` list. If these
attributes are of type **ProteinsPlusHashableModel** themselves this process continues recursively
until a final hash key is constructed. Then, the function searches the database for an existing job
object with this particular hash key. If it finds one, the found object is immediately returned
as the result to the user's request and the newer, not finished job object is deleted. If no
matching job object can be found, the job is stored in the database with it's generated hash key 
and the job is submitted for execution. If a job's execution ever fails, it's hash key is deleted
to make sure only successfully completed jobs are found by the caching system.

As described in the section about input **Models** and caching, the system supports most attribute
types as hash attributes. If you should ever encounter an unsupported attribute type, you can add
custom hashing behaviour inside the **proteins_plus/models.py** file. Only do this with explicit
need and permission.

# Deployment

The preferred deployment server is gunicorn. It can be installed like this:

```bash
conda install -c anaconda gunicorn
```

Two scripts, start.sh and stop.sh, are provided as utilities to start and stop all necessary
processes. These scripts are intended to be run from the project directory. The necessary
processes are the following:

- redis
- celery
- gunicorn
- a display server (emulated for example by TigerVNC)

Configurations of the individual components is kept as close to default as possible and modified
values in configuration files are marked with 'modified'.

## Start and Stop

The start script starts all necessary processes if they are not already running. Display servers
are started if none are available and one display is assigned to the `DISPLAY` environment
variable. All other processes are started if they're expected process ID (PID) files do not exist. If a
process is terminated irregularly it may leave a dead PID file behind, which may cause problems
when restarting the process. The stop script stops processes using their PID files. Display servers
are not managed by the stop script.

### Redis

Redis is the message passing framework that coordinates passing asynchronous jobs to celery
workers. A `redis/` directory containing a configuration has been provided. This configuration will
write all log output and all database dumps into the `redis/` directory.

### Celery

Celery is the asynchronous job processing framework. A directory structure for running and logging
has been provided that corresponds to the commands in the start script.

### Gunicorn

Gunicorn is the production python server that actually hanldes requests. A `gunicorn/` directory
containing a configuration has been provided. This configuration will write all log output into the
`gunicorn/` directory.

### Display server

A display server is necessary for SVG drawing functionality, which is present for ex. in the
preprocessor or PoseView. Checking whether a display is running and using that display is handled
in the start script.

## Clean

A clean script has been provided to be run periodically. It will clean up unused data and stale
cached objects. It is intended to be run from the project directory.
