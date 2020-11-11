Title: Sharing your machine learning models through a REST API
Date: 2020-11-11 10:00

Note: This blog post was originally published in [KDNuggets](https://www.kdnuggets.com/2020/02/sharing-machine-learning-models-common-api.html).

Data scientists building machine learning models do not have an easy and common
way to share their developed applications with their colleagues or with anybody
interested in using them. The whole model (i.e. the code and any configuration
assets needed) can be shared, but this requires that the receptors of the model
need to have enough knowledge to execute it. In most cases we just want to
share the model to show its functionality (to other colleagues or to a company
interested in our predictive model), therefore there is no need to share the
whole experiment.

The most straightforward way of doing so, in the connected world where we all
work, is to expose the model through an HTTP endpoint, so that potential users
can access it remotely through the network. This might sound simple, but
developing a proper and correct REST API is not an easy task. Data scientists
need to have knowledge on API programming, networking, REST semantics,
security, etc. Moreover, if every scientists comes up with an implementation,
we would end up with a myriad of different and non-interoperable APIs leading
doing more or less the same job, leading to a fragmented ecosystem.

Enter [DEEPaaS API](https://deepaas.readthedocs.io/): a machine learning, deep
learning and artificial intelligence REST API framework built using [aiohttp](https://docs.aiohttp.org/).
DEEPaaS is an software component that allows to expose the functionality of a
Python model (implemented with the framework of your choice) through an HTTP
endpoint. It requires no modification to the original code, and has methods to
customize it to the scientist's choice (input parameters, expected output,
etc.)

The DEEPaaS API follows the [OpenAPI Specification
(OAS)](https://www.openapis.org/), therefore it allows humans and computers to
discover and understand the capabilities of the underlying model, its input
parameters and output values, without inspecting the model's source code.

Lets see how it works with a walk-through example.

# Plugging a model into DEEPaaS

In order to better illustrate how to integrate a model with DEEPaaS we will use
one of the most known examples from [scikit-learn](https://scikit-learn.org/):
a [Support Vector Machine](https://scikit-learn.org/stable/modules/svm.html)
trained against the [IRIS
dataset](https://scikit-learn.org/stable/auto_examples/datasets/plot_iris_dataset.html#sphx-glr-auto-examples-datasets-plot-iris-dataset-py).
In this naïve example we are defining two different functions, one for training
and one for performing a prediction, as follows:

    :::python
    from joblib import dump, load
    import numpy
    from sklearn import svm
    from sklearn import datasets

    def train():
        clf = svm.SVC()
        X, y = datasets.load_iris(return_X_y=True)
        clf.fit(X, y)
        dump(clf, 'iris.joblib')

    def predict(data):
        clf = load('iris.joblib')
        data = numpy.array(data).reshape(1, -1)
        prediction = clf.predict(data)
        return {"labels": prediction.tolist()}

As you can see, the training function persists into disk the trained model,
following the [scikit-learn's
tutorial](https://scikit-learn.org/stable/tutorial/basic/tutorial.html#model-persistence).
The next action is to define the input parameters for your train and predict
calls. Since this example is quite simple, we are only defining input
parameters for the prediction call. Normally you would need to make it in
a different file, so that it does not interfere with your code, but for the
sake of simplicity we are adding this special function alongside our IRIS SVM:

    :::python
    from joblib import dump, load
    import numpy
    from sklearn import svm
    from sklearn import datasets
    from webargs import fields, validate

    def train():
        clf = svm.SVC()
        X, y = datasets.load_iris(return_X_y=True)
        clf.fit(X, y)
        dump(clf, 'iris.joblib')

    def predict(data):
        clf = load('iris.joblib')
        data = numpy.array(data).reshape(1, -1)
        prediction = clf.predict(data)
        return {"labels": prediction.tolist()}

    def get_predict_args():
        args = {
            "data": fields.List(
                fields.Float(),
                required=True,
                description="Data to make a prediction. The IRIS dataset expects "
                            "for values containing the Sepal Length, Sepal Width, "
                            "Petal Length and Petal Width.",
                validate=validate.Length(equal=4),
            ),
        }
        return args

The last step in order to integrate it with DEEPaaS API you need to make it
installable (you should be doing so) and define an entry point using [Python's
setuptools](https://docs.python.org/3.8/distutils/setupscript.html). This entry
point will be used by DEEPaaS to know that to load and how to plug the
different functions to the defined endpoints. We are currently using the
`deepaas.model.v2` entry point namespace, therefore we can create the
`setup.py` file as follows:

    :::python
    from distutils.core import setup

    setup(
        name='test-iris-with-deepaas',
        version='1.0',
        description='This is an SVM trained with the IRIS dataset',
        author='Álvaro López',
        author_email='aloga@ifca.unican.es',
        py_modules="iris-deepaas.py",
        dependencies=['joblib', 'scikit-learn'],
        entry_points={
            'deepaas.v2.model': ['iris=iris-deepaas'],
        }
    )

# Installing and running DEEPaaS

Once you have your code ready, you simply need to install both your module and
the DEEPaaS API so that it detects it and exposes its functionality through the
API. In order to do so in an easy way, lets create a virtualenv and install
everything inside:

    :::bash
    $ virtualenv env --python=python3
        (...)
    $ source env/bin/activate
    (env) $ pip3 install .
        (...)
    (env) $ pip3 install deepaas
        (...)
    (env) $ deepaas-run

             ##         ###
             ##       ######  ##
         .#####   #####   #######.  .#####.
        ##   ## ## //   ##  //  ##  ##   ##
        ##. .##  ###  ###   // ###  ##   ##
          ## ##    ####     ####    #####.
                  Hybrid-DataCloud  ##


    Welcome to the DEEPaaS API API endpoint. You can directly browse to the
    API documentation endpoint to check the API using the builtint Swagger UI
    or you can use any of our endpoints.

        API documentation: http://127.0.0.1:5000/ui
        API specification: http://127.0.0.1:5000/swagger.json
              V2 endpoint: http://127.0.0.1:5000/v2

    -------------------------------------------------------------------------

    2020-02-04 13:10:50.027 21186 INFO deepaas [-] Starting DEEPaaS version 1.0.0
    2020-02-04 13:10:50.231 21186 INFO deepaas.api [-] Serving loaded V2 models: ['iris-deepaas']

# Accessing the API and making trainings and predictions

If everything was OK now you should be able to point your browser to the URL
printed in the console (`http://127.0.0.1:5000/ui`) and get a nice looking
[Swagger UI](https://swagger.io/tools/swagger-ui/) that will allow you to
interact with your model.

Since this was a simple example, we have not shipped a trained model, so the
first thing to do is to perform a training. This will call the `train()`
function and save the trained SVM for later use. You can do it from the UI, or
from a command line with:

    :::bash
	curl -s -X POST "http://127.0.0.1:5000/v2/models/iris-deepaas/train/" -H  "accept: application/json" | python -mjson.tool
	{
		"date": "2020-02-04 13:14:49.655061",
		"uuid": "16a3141af5674a45b61cba124443c18f",
		"status": "running"
	}

The training will be done asynchronously, so that the API does not block. You
can check its status from the UI, or with the following call:

    :::bash
	curl -s -X GET "http://127.0.0.1:5000/v2/models/iris-deepaas/train/" | python -mjson.tool
	[
 		{
			"date": "2020-02-04 13:14:49.655061",
			"uuid": "16a3141af5674a45b61cba124443c18f",
			"status": "done"
		}
	]

Now that the model is trained, we can perform a prediction. The IRIS dataset
consists of 3 different types of irises' (Setosa, Versicolour, and Virginica)
petal and sepal length. The samples have four columns that correspond to the
Sepal Length, Sepal Width, Petal Length and Petal Width. In our example lets
try to get the results for the `[5.1. 3.5, 1.4, 0.2]` observation, and get the
results. Once again, you can make it from the UI or from the command line as
follows:

    :::bash
	curl -s -X POST "http://127.0.0.1:5000/v2/models/iris-deepaas/predict/?data=5.1&data=3.5&data=1.4&data=0.2" -H  "accept: application/json" | python -mjson.tool
	{
	    "predictions": {
	        "labels": [
	            0
	        ]
	    },
	    "status": "OK"
	}

As you can see, the results contains the prediction that our SVM performed. In
this case, the label for the input data was `0`, that is, indeed, the correct
one.

# Conclusions

In this simple example we have shown how a machine learning practitioner can
expose any Python-based model through a REST API relying on the DEEPaaS API,
rather than developing their own home-brew API. By doing so, data scientist
can focus on their work, without worrying about writing and developing complex
REST applications. Moreover, by using a common API, different modules will
share the same interface, making it easier to be deployed in production and
utilized by different programmers.
