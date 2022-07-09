workspace {

    model {
        !include model/page.dsl
        !include model/people.dsl
        !include model/story.dsl

        !include relationship/fundamentals.dsl
    }

    views {
        !include view/fundamentals.dsl

        styles {
            element "Person" {
                shape "person"
            }

            element "Relationship" {
                border "solid"
            }
        }
    }

}