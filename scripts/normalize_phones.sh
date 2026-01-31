#!/bin/bash

# Script to normalize Ukrainian phone numbers in the database to +380 format
# Usage: ./normalize_phones.sh [--dry-run]

set -e

DRY_RUN=false

if [ "$1" = "--dry-run" ]; then
    DRY_RUN=true
    echo "🔍 DRY RUN MODE - No changes will be made to the database"
else
    echo "⚠️  LIVE MODE - Database will be updated"
    read -p "Continue? [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
fi

if [ ! -f ".env" ]; then
    echo "Error: .env file not found"
    exit 1
fi

export $(grep -v '^#' .env | xargs)

if [ -z "$DB_HOST" ] || [ -z "$POSTGRES_DB" ] || [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_PASSWORD" ]; then
    echo "Error: Database configuration not found in .env"
    echo "Required variables: DB_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_PORT"
    exit 1
fi

POSTGRES_PORT=${POSTGRES_PORT:-5432}

export PGPASSWORD="$POSTGRES_PASSWORD"

echo ""
echo "Connecting to database $POSTGRES_DB at $DB_HOST:$POSTGRES_PORT..."
echo "=========================================="

SQL_SCRIPT=$(cat <<'EOF'
DO $$
DECLARE
    phone_record RECORD;
    original_number TEXT;
    cleaned TEXT;
    normalized TEXT;
    total_count INT := 0;
    updated_count INT := 0;
    skipped_count INT := 0;
    error_count INT := 0;
BEGIN
    SELECT COUNT(*) INTO total_count FROM client_phones;
    RAISE NOTICE 'Found % phone numbers in database', total_count;
    RAISE NOTICE '================================================================================';

    FOR phone_record IN SELECT id, number FROM client_phones LOOP
        original_number := phone_record.number;

        cleaned := REGEXP_REPLACE(original_number, '[^\d+]', '', 'g');

        IF cleaned ~ '^\+' THEN
            cleaned := '+' || REPLACE(SUBSTRING(cleaned FROM 2), '+', '');
        ELSE
            cleaned := REPLACE(cleaned, '+', '');
        END IF;

        IF cleaned ~ '^\+380' THEN
            normalized := cleaned;
        ELSIF cleaned ~ '^380' THEN
            normalized := '+' || cleaned;
        ELSIF cleaned ~ '^0' THEN
            normalized := '+380' || SUBSTRING(cleaned FROM 2);
        ELSE
            normalized := '+380' || cleaned;
        END IF;

        IF LENGTH(normalized) = 13 AND SUBSTRING(normalized FROM 5) ~ '^\d+$' THEN
            IF normalized != original_number THEN
                updated_count := updated_count + 1;
                RAISE NOTICE '[UPDATED] ID %: ''%'' -> ''%''',
                    phone_record.id, original_number, normalized;

                UPDATE client_phones
                SET number = normalized
                WHERE id = phone_record.id;
            ELSE
                skipped_count := skipped_count + 1;
            END IF;
        ELSE
            error_count := error_count + 1;
            RAISE NOTICE '[ERROR] ID %: Could not normalize ''%'' (invalid format)',
                phone_record.id, original_number;
        END IF;
    END LOOP;

    RAISE NOTICE '================================================================================';
    RAISE NOTICE 'Summary:';
    RAISE NOTICE '  Total phone numbers: %', total_count;
    RAISE NOTICE '  Updated: %', updated_count;
    RAISE NOTICE '  Already correct: %', skipped_count;
    RAISE NOTICE '  Errors: %', error_count;
END $$;
EOF
)

if [ "$DRY_RUN" = true ]; then
    SQL_WRAPPED="BEGIN; $SQL_SCRIPT ROLLBACK;"
    echo "Note: Changes will be rolled back (dry run)"
    echo ""
else
    SQL_WRAPPED="BEGIN; $SQL_SCRIPT COMMIT;"
fi

docker exec -e PGPASSWORD="$POSTGRES_PASSWORD" water_delivery-postgres \
    psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "$SQL_WRAPPED" 2>&1

unset PGPASSWORD

echo ""
echo "Done!"