

<section id="description">

# Standardized Region  (universal)



## Description


[View in HTML](https://wcrp-cmip.github.io/CF/standardized-region/standardized-region)

</section>



<section id="info">


| Item | Reference |
| --- | --- |
| Type | `wrcp:standardized-region` |
| Pydantic class | [`False`](https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/False.py):  Not yet implemented |
| | |
| JSON-LD | `cf:standardized-region` |
| Expanded reference link | [https://wcrp-cmip.github.io/CF/standardized-region](https://wcrp-cmip.github.io/CF/standardized-region) |
| Developer Repo | [![Open in GitHub](https://img.shields.io/badge/Open-GitHub-blue?logo=github&style=flat-square)](https://github.com/WCRP-CMIP/CF/tree/main/src-data/standardized-region) |


</section>
    <section id='links'>

## 🔗 Links

No context file found!!!</section> 


<section id="schema">

## Content Schema

- **`id`**  
   [**unknown**]
  No Pydantic model found.
- **`validation-key`**  
   [**unknown**]
  No Pydantic model found.
- **`ui-label`**  
   [**unknown**]
  No Pydantic model found.
- **`description`**  
   [**unknown**]
  No Pydantic model found.
- **`cf-name`**  
   [**unknown**]
  No Pydantic model found.
- **`@context`**  
   [**unknown**]
  No Pydantic model found.
- **`type`**  
   [**unknown**]
  No Pydantic model found.





</section>   

<section id="usage">

## Usage

### Online Viewer 
To view a file in a browser use the content link with `.json` appended. 
eg. https://github.com/WCRP-CMIP/CF/tree/main/src-data/standardized-region/africa.json

### Getting a File. 

A short example of how to integrate the computed ld file into your code. 

```python

import cmipld
cmipld.get( "cf:standardized-region/africa")

```

### Framing
Framing is a way we can filter the downloaded data to match what we want. 
```python
frame = {
            "@context": "https://wcrp-cmip.github.io/CF/standardized-region/_context_",
            "@type": "wcrp:standardized-region",
            "keys we want": "",
            "@explicit": True

        }
        
import cmipld
cmipld.frame( "cf:standardized-region/africa" , frame)

```
</section>

    