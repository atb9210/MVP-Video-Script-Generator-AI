# Generate Image

> Use [CogView-4](/guides/image/cogview-4) series models to generate high-quality images from text prompts. `CogView-4-250304` is suitable for image generation tasks, with quick and accurate understanding of user text descriptions to let `AI` express images more precisely and personally.



## OpenAPI

````yaml POST /paas/v4/images/generations
openapi: 3.0.1
info:
  title: Z.AI API
  description: Z.AI API available endpoints
  license:
    name: Z.AI Developer Agreement and Policy
    url: https://chat.z.ai/legal-agreement/terms-of-service
  version: 1.0.0
  contact:
    name: Z.AI Developers
    url: https://chat.z.ai/legal-agreement/privacy-policy
    email: user_feedback@z.ai
servers:
  - url: https://api.z.ai/api
    description: Production server
security:
  - bearerAuth: []
paths:
  /paas/v4/images/generations:
    post:
      summary: Generate Image
      description: >-
        Use [CogView-4](/guides/image/cogview-4) series models to generate
        high-quality images from text prompts. `CogView-4-250304` is suitable
        for image generation tasks, with quick and accurate understanding of
        user text descriptions to let `AI` express images more precisely and
        personally.
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateImageRequest'
            examples:
              Generate Image Example:
                value:
                  model: cogView-4-250304
                  prompt: >-
                    A cute little kitten sitting on a sunny windowsill, with the
                    background of blue sky and white clouds.
                  size: 1024x1024
        required: true
      responses:
        '200':
          description: Processing successful
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ImageGenerationResponse'
        default:
          description: Request Failed
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
components:
  schemas:
    CreateImageRequest:
      type: object
      required:
        - model
        - prompt
      properties:
        model:
          type: string
          description: Model code
          enum:
            - cogview-4-250304
          example: cogview-4-250304
        prompt:
          type: string
          description: The text description of the image to be generated.
          example: A cute little kitten.
        quality:
          type: string
          description: >-
            The quality of the generated image. Default is `standard`. `hd`:
            Generates a more detailed and rich image with higher overall
            consistency, but takes about `20` seconds. `standard`: Generates an
            image quickly, suitable for scenarios with higher requirements for
            generation speed, takes about `5-10` seconds. This parameter is only
            supported for `cogview-4-250304`.
          enum:
            - hd
            - standard
          default: standard
        size:
          type: string
          description: >-
            Image size, default is `1024x1024`, recommended enum values:
            `1024x1024` (default), `768x1344`, `864x1152`, `1344x768`,
            `1152x864`, `1440x720`, `720x1440`.

            Custom parameter: Both width and height must be between
            `512px-2048px`, and must be divisible by `16`, and the maximum pixel
            count must not exceed `2^21px`.
          default: 1024x1024
          example: 1024x1024
        user_id:
          type: string
          description: >-
            Unique ID of the end user, helping the platform intervene in illegal
            activities, inappropriate content generation, or other abuses. ID
            length: 6 to 128 characters.
          minLength: 6
          maxLength: 128
    ImageGenerationResponse:
      type: object
      properties:
        created:
          type: integer
          example: 1760335349
          description: Request creation time, in `Unix` timestamp format, unit is seconds.
        data:
          type: array
          description: >-
            Array, containing the generated image `URL`. Currently, the array
            only contains one image.
          items:
            type: object
            properties:
              url:
                type: string
                description: >-
                  Image link. The temporary link expires after `30` days, please
                  store it promptly.
            required:
              - url
        content_filter:
          type: array
          description: Array, containing content safety related information.
          items:
            type: object
            properties:
              role:
                type: string
                description: >-
                  Safety enforcement stage, including `role = assistant` model
                  inference, `role = user` user input, `role = history`
                  historical context.
                enum:
                  - assistant
                  - user
                  - history
              level:
                type: integer
                description: >-
                  Severity level `level 0-3`, `level 0` is most severe, `3` is
                  least severe.
                minimum: 0
                maximum: 3
    Error:
      required:
        - code
        - message
      type: object
      description: The request has failed.
      properties:
        code:
          type: integer
          format: int32
          description: Error code.
        message:
          type: string
          description: Error message.
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      description: >-
        Use the following format for authentication: Bearer [<your api
        key>](https://z.ai/manage-apikey/apikey-list)

````

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.z.ai/llms.txt