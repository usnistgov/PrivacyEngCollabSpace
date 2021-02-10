# NIST: Differential Privacy Synthetic Data Challenge #3
## Competitor Pack
### Content

1.  Challenge dataset:

    1.  [`data/colorado.csv`](data/colorado.csv) - The main dataset to be
        privatized.

    2.  [`data/colorado-specs.json`](data/colorado-specs.json) - The important
        part of the dataset's data dictionary.

    3.  [`data/NISTChallengeMatch3DataDict.txt`](data/NISTChallengeMatch3DataDict.txt)
        - Data dictionary - Briefly explains all columns included into the dataset,
				and contains links to the detailed explanations.

    4.  [`data/codebook.cbk`](data/codebook.cbk) - Dataset codebook - Contains, among
				other stuff, legend for possible values of categorical columns. This is
				the original codebook for US-wide Census Data, thus some of information
				included there, is not applicable to this match, where only single state
				data are used as input.

2.  Sample Python scripts:

    1.  [`scripts/simple-dp.py`](scripts/simple-dp.py) - A sample naive
        implementation of a simple differential data privacy algorithm.

    2.  [`scripts/generate-submission.py`](scripts/generate-submission.py) -
        An auxiliary script for preparation of submissions into Topcoder system.

    3.  [`scripts/generate-ground-truth-1.py`](scripts/generate-ground-truth-1.py)
        \- The stochastic ground-truth generator for the first scoring method.

    4.  [`scripts/generate-ground-truth-2.py`](scripts/generate-ground-truth-2.py)
        \- The stochastic ground-truth generator for the second scoring method.

    5.  [`scripts/generate-ground-truth-3.py`](scripts/generate-ground-truth-3.py)
        \- The stochastic ground-truth generator for the second scoring method.

    7.  [`scripts/test-scoring.py`](scripts/test-scoring.py) - A Python
        implementation of the core scoring logic.

### Challenge Dataset

**The dataset to be privatized** in this challenge is provided in CSV format:
[`data/colorado.csv`](data/colorado.csv). It is Public Use Microdata Sample
(PUMS) of 1940's USA Census Data for Colorado State. You can find the detailed
explanation of each column at the
[IPUMS USA Website](https://usa.ipums.org/usa/1940CensusDASTestData.shtml); also
the [`data/codebook.cbk`](data/codebook.cbk) document contains definition of all
possible values in categorical columns. A few notes:

- Some of the columns mentioned at the website and in the codebook were not
  included into the dataset to use in this match;

- We trimmed leading zeros from all codes in the dataset; i.e. instead of a
  code value `000` specified in the codebook, you will find just `0` in the
  `colorado.csv` dataset; `1` instead of `01`, etc.

- For numerical columns the values like `99998` correpond to the `N/A` value
  (the original dataset was distributed in the fixed column width format; for
  convenience of use we converted it to CSV; the `N/A` value in a certain
  column has as many `9` digits as necessary for the value to fill the full
  width of the original column).

- To keep similarity with the previous matches, `data/colorado-specs.json` file
  is provided, and it describes all columns included into the dataset to be
  privatized. Unlike in the previous matches, this time, for scoring purposes,
  we consider all columns as categoric, hence `enum` type (the dataset also has
  numeric columns with integer values, that naturally can be treated as
  categorical). Unlike in the previous challenges, the values of categorical
  columns are not restricted to continious ranges from `0` to `count - 1`, where
  `count` values are given in `data/colorado-specs.json`. The `count` values in
  this case specify the total number of distinct values we found in each column
  of the dataset; and `maxval` specifies the maximum value we found in each
  column.

### Sample Python Scripts

Six Python 3 scripts are provided in the `script` folder of this competitor
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
  _epsilon_ values 8.0; 1.0; and 0.3, required by the challenge rules;

- Checks that resulting output files, `8_0.csv`, `1_0.csv`, and `0_3.csv`
  satisfy the size limit (350 Mb max per file);

- Pack output files into ZIP archive with the specified name, and checks that
  the resulting ZIP file also satisfies the 350 Mb size limit.

Resulting ZIP file should be uploaded to a file hosting, supporting direct
download URLs. For example, Google.Drive supports them, if you get share link
and replace its `open` piece by `uc`, like so:

`https://drive.google.com/uc?id=1JV3R0fZALeqhA8DRUSscnT1GN94cGf-N`

The resulting URL should be wrapped in the following piece of Java code, which
you submit into Topcoder system:

```java
class NistDp3 {
  public String getAnswerUrl() {
    return "https://drive.google.com/uc?id=1JV3R0fZALeqhA8DRUSscnT1GN94cGf-N";
  }
}
```

Run the script as 

`$ ./scripts/generate-submission.py scripts/simple-dp.py data/colorado-data.csv output.zip data/colorado-specs.json 7`

where the second argument is the command to run your algorithm from the command
line; and 7 is the number of columns to handle, which will be passed down into
your algorithm.

---

For the local testing you are provided with three **ground-truth generators**
[`scripts/generate-ground-truth-1.py`](scripts/generate-ground-truth-1.py),
[`scripts/generate-ground-truth-2.py`](scripts/generate-ground-truth-2.py), and
[`scripts/generate-ground-truth-3.py`](scripts/generate-ground-truth-3.py).
First two generators produce randomized sets of scoring tests for the first
two scoring methods being used in this match, the third one calculates the test
set for the third scoring method (this test set is determenistic). All these
test sets can be fed into the _test scoring_ script below. Similarly generated
sets of scoring tests are used for provisional and system scoring of the callenge.
Run these scripts as:

`$ ./scripts/generate-ground-truth-1.py data/colorado-data.csv data/colorado-specs.json gt-1.csv`

`$ ./scripts/generate-ground-truth-2.py data/colorado-data.csv data/colorado-specs.json gt-2.csv`

`$ ./scripts/generate-ground-truth-3.py data/colorado-data.csv data/colorado-specs.json gt-3.csv`

A single CSV file, containing a privatized dataset (or its subset, consisting of
_N_ first columns), can be fed together with the generated ground truth files,
into the local **test scoring script**
[`scripts/test-scoring.py`](scripts/test-scoring.py), in the following manner:

`$ ./scripts/test-scoring.py privatized-dataset.csv data/colorado-specs.json gt-1.csv gt-2.csv gt-3.csv`

The scoring script detects the number of columns automatically, and returns the
score in the range from 0 to 1 000 000 (corresponds to a fully processed dataset,
that ideally conserves records distributions).

During the provisional scoring, the scores from three generated datasets
(for _epsilon_ = 8.0; 1.0; 0.3) are averaged.

See challenge rules for detailed information on the scoring procedure.
