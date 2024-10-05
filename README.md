# CTINexus
<p align="center">
    <br>
    <img src="Knowledge-Graph.webp" width="70"/>
    <br>
</p>
LLM-empowered CTI information extraction (IE) and knowledge graph construction (KGC) framework.

## Components
* `main.py` is the entry file for every component and sub-component.
  - As we are using the `hydra` library to config the pipeline, please edit the configuration parameters in the `main.py` to try out different configurations.
  - Where?
    - `@hydra.main(config_path="config", config_name="demoNum=4", version_base="1.2")`
    - `config` folder under the `IE`, `KGC/Tagger`, `KGC/Merger` and `KGC/Linker` repos.
      - Please note that different configurations need to apply different configuration files, you can specify which configuration file to apply in the `main.py`
### IE - information extraction
 * extract triplets according to the applied ontology
 *  Where to apply ontology?
     * `Toolbox/IE_Prompts/QD1.jinja`
       * You can change the applied ontology in the prompt file.
### KGC - knowledge graph construction
 * Tagger - tagging entity with corresponding types
 * Merger - merge entities within the same type with high semantic similarity
 * Linker - link distant related entities according to the context


