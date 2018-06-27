

#
db.getCollection('test_stats').aggregate([
{$match: {}},
{$group: {_id: "$genome_id", total: {$sum: "$1_comprehended"}}}

])


# Exposed vs. comprehended numbers
﻿db.getCollection('test_stats').aggregate([
{$match: {}},
{$group: {_id: "$genome_id",    total_exposed_0: {$sum: "$0_exposed"}, total_comprehended_0: {$sum: "$0_comprehended"},
                                total_exposed_1: {$sum: "$1_exposed"}, total_comprehended_1: {$sum: "$1_comprehended"},
                                total_exposed_2: {$sum: "$2_exposed"}, total_comprehended_2: {$sum: "$2_comprehended"},
                                total_exposed_3: {$sum: "$3_exposed"}, total_comprehended_3: {$sum: "$3_comprehended"},
                                total_exposed_4: {$sum: "$4_exposed"}, total_comprehended_4: {$sum: "$4_comprehended"},
                                total_exposed_5: {$sum: "$5_exposed"}, total_comprehended_5: {$sum: "$5_comprehended"},
                                total_exposed_6: {$sum: "$6_exposed"}, total_comprehended_6: {$sum: "$6_comprehended"},
                                total_exposed_7: {$sum: "$7_exposed"}, total_comprehended_7: {$sum: "$7_comprehended"},
                                total_exposed_8: {$sum: "$8_exposed"}, total_comprehended_8: {$sum: "$8_comprehended"},
                                total_exposed_9: {$sum: "$9_exposed"}, total_comprehended_9: {$sum: "$9_comprehended"}}}
])


# fitness greater than a number listed descending
db.genomes.find({"fitness": {$gt: 0.2}}).sort({fitness: -1})

or

﻿db.genomes.aggregate([
    {$match: {"fitness": {$gt: 0.2}}},
    {$sort: {fitness: -1}}
])



# listing all fitnesses above a threshold
﻿db.genomes.aggregate([
    {$match: {"fitness": {$gt: 0.2}}},
    {$group: {_id: "$fitness"}},
    {$sort: {_id: -1}}
])


# field exist
﻿db.getCollection('genomes').aggregate([
{$match: {fitness: {$exists: true}}},
{$project: {"genome_id": 1, "fitness": 1}}
])


