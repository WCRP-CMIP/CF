

<section id="description">

# Area Type Table  (universal)



## Description


[View in HTML](https://wcrp-cmip.github.io/CF/area-type-table/area-type-table)

</section>



<section id="info">


| Item | Reference |
| --- | --- |
| Type | `wrcp:area-type-table` |
| Pydantic class | [`False`](https://github.com/ESGF/esgf-vocab/blob/main/src/esgvoc/api/data_descriptors/False.py):  Not yet implemented |
| | |
| JSON-LD | `cf:area-type-table` |
| Expanded reference link | [https://wcrp-cmip.github.io/CF/area-type-table](https://wcrp-cmip.github.io/CF/area-type-table) |
| Developer Repo | [![Open in GitHub](https://img.shields.io/badge/Open-GitHub-blue?logo=github&style=flat-square)](https://github.com/WCRP-CMIP/CF/tree/main/src-data/area-type-table) |


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
eg. https://github.com/WCRP-CMIP/CF/tree/main/src-data/area-type-table/air.json

### Getting a File. 

A short example of how to integrate the computed ld file into your code. 

```python

import cmipld
cmipld.get( "cf:area-type-table/air")

```

### Framing
Framing is a way we can filter the downloaded data to match what we want. 
```python
frame = {
            "@context": "https://wcrp-cmip.github.io/CF/area-type-table/_context_",
            "@type": "wcrp:area-type-table",
            "keys we want": "",
            "@explicit": True

        }
        
import cmipld
cmipld.frame( "cf:area-type-table/air" , frame)

```
</section>

    