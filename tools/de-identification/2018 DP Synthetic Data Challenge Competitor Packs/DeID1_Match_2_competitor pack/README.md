# NIST: Differential Privacy Synthetic Data Challenge #2
## Competitor Pack
### Content

1.  Challenge dataset:

    1.  [`data/2016-data.csv`](data/2016-data.csv) - The main dataset to be
        privatized.

    2.  [`data/2016-specs.json`](data/2016-specs.json) - The important
        part of the dataset's data dictionary.

    3.  [`data/2016-specs-mapping.json`](data/2016-specs-mapping.json)
        \- An auxiliary part of the dataset's data dictionary (not required for
        the challenge scope).

2.  Sample Python scripts:

    1.  [`scripts/simple-dp.py`](scripts/simple-dp.py) - A sample naive
        implementation of a simple differential data privacy algorithm.

    2.  [`scripts/generate-submission.py`](scripts/generate-submission.py) -
        An auxiliary script for preparation of submissions into Topcoder system.

    3.  [`scripts/generate-ground-truth-1.py`](scripts/generate-ground-truth-1.py)
        \- The stochastic ground-truth generator for the first scoring method.

    4.  [`scripts/generate-ground-truth-2.py`](scripts/generate-ground-truth-2.py)
        \- The stochastic ground-truth generator for the second scoring method.

    4.  [`scripts/test-scoring.py`](scripts/test-scoring.py) - A Python
        implementation of the core scoring logic.

### Challenge Dataset

**The dataset to be privatized** in this challenge is provided in CSV format:
[`data/2016-data.csv`](data/2016-data.csv). It is a subset of
[San Francisco's Fire Deparment Call for Service dataset](https://data.sfgov.org/Public-Safety/Fire-Department-Calls-for-Service/nuek-vuh3),
reduced to data for the year 2016 only. For the sake of simplicity all original
data values were converted to numeric formats in the following ways:

- Categorical values (string literals) were replaced by consequitive integer
  numbers from 0 (inclusive) to _N_ (exclusive), where _N_ is the total number of
  possible values. The columns containing such data are denoted by `enum` type
  in the data dictionary JSON file
  [`data/2016-specs.json`](`data/2016-specs.json), where _N_ values
  are also given in the _count_ fields.

  The additional JSON document
  [`data/2016-specs-mapping.json`](data/2016-specs-mapping.json)
  provides, for columns with categorical values, the mappings between resulting
  integer values and the original data. Though, this information is provided for
  curiousity, and it is not necessary for the challenge purposes.

- Date/time values were parsed and converted into integer Unix timestamps
  (number of seconds from 00:00:00 UTC, January 1, 1970). Such columns, along
  with originally integer columns, are denoted by `integer` type in the data
  dictionary file. The range of their possible values is given by _min_ and
  _max_ fields in there (both inclusive). The additional _optional_ (boolean)
  field tells whether empty values might be present in corresponding columns.

- The column with geographical coordinates was split into two separate columns
  containing real numbers for lattitude and longitude. Each of resulting columns
  is denoted by `float` type in the data dictionary, with _min_ and _max_
  values provided.

Data columns in the [`data/2016-data.csv`](data/2016-data.csv) dataset were
sorted in such way that sizes of value domains for each column increase from
the first two the last column; i.e. the first and second columns contain
categorical data with two possible values; 3-rd column contains categorical
data with 5 possible values; etc. Numerical (both integer and float) columns
are placed along with the categorical data columns containing 100 possible
values.

---

**The data dictionary** is provided in JSON format
[data/2016-specs.json](data/2016-specs.json). As explained above,
for each column it provides data type in _type_ fields. There are three cases:

- `enum` type denotes columns with categorical data. The _count_ field provides
  the number of possible values in each of such columns; and the possible values
  themselves are from 0 (inclusive) to _N_ (exclusive).

- `integer` and `float` types denote columns with integer and float values. In
  both cases, the dictionary provides their _min_ and _max_ values (both
  inclusive); along with _optional_ boolean field, which tells whether the value
  is optional (may be empty). For the columns with _optional_ equal `false`, each
  record in the dataset must have a numeric value; while for the columns with
  _optional_ field equal `true` a record may have either numeric value, or to
  be empty.

**The auxiliary part of the data dictionary**
[`data/fire-data-specs-mapping.json`](data/fire-data-specs-mapping.json) is
provided for curiosity, and it is not necessary for the purpose of this
challenge. It contains mappings between integer codes and original literal
values of categorical (`enum`) columns.

### Sample Python Scripts

Five Python 3 scripts are provided in the `script` folder of this competitor
pack. They were tested on Ubuntu 18.04, and might require slight modifications
to work on MacOS or Windows machines. There is dependency on `numpy` package,
you can run install it with `$ pip3 install numpy` command.

**A sample naive implementation of a simple _epsilon_ differential data privacy**
algorithm is provided by [`scripts/simple-dp.py`](scripts/simple-dp.py).
Example usage is (all paths below are relative to the root of competitor
pack):

`$ ./scripts/simple-dp.py data/fire-data.csv privatized-dataset.csv data/fire-data-specs.json 1.0 7`

where 1.0 is the _epsilon_ value and 7 is the number of data columns to handle
(see the challenge scoring details in the challenge rules). This algorithm
assumes _delta_ equal to zero. As the algorithm is really naive, it is not
a good idea to run it for a number of columns larger than 10 (it will require
too much memory, and will run too long).

---

**An auxiliary script for preparation of Topcoder submission** is provided in
[`scripts/generate-submission.py`](scripts/generate-submission.py). For a
differential data privacy algorithm, exposed via the same command line interface
as the sample algorithm above, it:

- Runs the algorithm, on the specified number of columns, three times with
  _epsilon_ values 1.0; 1.0; and 0.01, required by the challenge rules;

- Checks that resulting output files, `1_0.csv`, `1_0.csv`, and `0_01.csv`
  satisfy the size limit (100 Mb max per file);

- Pack output files into ZIP archive with the specified name.

Resulting ZIP file should be uploaded to a file hosting, supporting direct
download URLs. For example, Google.Drive supports them, if you get share link
and replace its `open` piece by `uc`, like so:

`https://drive.google.com/uc?id=1MUMH0IZ3-zgfLYloFXvOrhA4EpKgEBrl`

The resulting URL should be wrapped in the following piece of Java code, which
you submit into Topcoder system:

```java
class NistDp1 {
  public String getAnswerUrl() {
    return "https://drive.google.com/uc?id=1MUMH0IZ3-zgfLYloFXvOrhA4EpKgEBrl";
  }
}
```

Run the script as 

`$ ./scripts/generate-submission.py scripts/simple-dp.py data/2016-data.csv output.zip data/2016-specs.json 7`

where the second argument is the command to run your algorithm from the command
line; and 7 is the number of columns to handle, which will be passed down into
your algorithm.

---

For local testing you are provided with two **stochastic ground-truth generators**
[`scripts/generate-ground-truth-1.py`](scripts/generate-ground-truth-1.py), and
[`scripts/generate-ground-truth-2.py`](scripts/generate-ground-truth-2.py).
Each run of the generators produces randomized sets of scoring tests for two
scoring methods being used in this match, to be feeded into the _test scoring_
script below. Similarly generated sets of scoring tests are used for provisional
and system scoring of the challenge. Run these scripts as:

`$ ./scripts/generate-ground-truth-1.py data/2016-data.csv data/2016-specs.json gt-1.csv`

`$ ./scripts/generate-ground-truth-2.py data/2016-data.csv data/2016-specs.json gt-2.csv`

A single CSV file, containing a privatized dataset (or its subset, consisting of
_N_ first columns), can be fed together with the generated ground truth files,
into the local **test scoring script**
[`scripts/test-scoring.py`](scripts/test-scoring.py), in the following manner:

`$ ./scripts/test-scoring.py privatized-dataset.csv data/2016-specs.json gt-1.csv gt-2.csv`

The scoring script detects the number of columns automatically, and returns the
score in the range from 0 to 1 000 000 (corresponds to a fully processed dataset,
that ideally conserves records distributions).

During the provisional scoring, the scores from three generated datasets
(for _epsilon_ = 1.0; 0.1; 0.01) are averaged.

See challenge rules for detailed information on the scoring procedure.
