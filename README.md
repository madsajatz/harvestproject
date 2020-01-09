# harvestproject
This play's in a CSA = COMMUNITY SUPPORTED AGRICULTURE environment.<br>
It started with the idea to collect crop data via html to spit it out in any Exel-format desired.<br>
And this Idea is somehow still alive, Vegetables gardening note tool.<br>
#### System
Postgres Python3 Flask SQLAlchemy WTForms Jinja2 HTML ZURB-Foundation jQuery
#### Model (a game of erp)
Per database/subDomain there is one adjacency list of products and one adjacency list of factions, separation of concerns, 
implied Usr highness groups. One database per subdomain maintenance nightmare. The shortest time period is 1 Day.<br>
There are resources and processments like soil and vegetables gardening. A "business logic" may be registered to a faction.<br>
A user is member of a faction in the first place to operate the logic. While processing the business logic, products appear. In my case vegetables to be harvested.<br>
A amount of a product can be transferred from one faction to another. From "vegetables gardening" to "members of the community" every friday, or from "vegetables gardening" to "vegetables gardening" to monitor daily crops.

The  model is glued to PostgreSQL and breaks referential integrity by allowing nested sets of primary keys<br>
from different tables in one relation as well as array(of,foreign,keys).<br>

